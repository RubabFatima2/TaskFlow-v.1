from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        # Store active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected")

    async def send_notification(self, user_id: int, message: dict):
        """Send notification to all connections for a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, user_id)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket endpoint for real-time notifications"""
    user_id = None
    try:
        # Try to get user from query parameter or cookies
        from app.utils.security import verify_token
        from app.database import get_session
        from app.models.user import User
        from sqlmodel import select

        # Try query parameter first, then cookies
        access_token = token or websocket.cookies.get("access_token")

        if not access_token:
            logger.warning(f"WebSocket connection attempt without access token. Query token: {token}, Cookies: {list(websocket.cookies.keys())}")
            await websocket.close(code=1008, reason="Not authenticated")
            return

        logger.info(f"Access token found, verifying...")
        payload = verify_token(access_token)
        if payload is None:
            logger.warning("WebSocket connection attempt with invalid token")
            await websocket.close(code=1008, reason="Invalid token")
            return

        user_id = payload.get("user_id")
        if user_id is None:
            logger.warning("WebSocket connection attempt with invalid token payload")
            await websocket.close(code=1008, reason="Invalid token payload")
            return

        logger.info(f"Token verified for user {user_id}, checking database...")

        # Verify user exists
        async for session in get_session():
            statement = select(User).where(User.id == user_id)
            result = await session.execute(statement)
            user = result.scalar_one_or_none()

            if user is None:
                logger.warning(f"WebSocket connection attempt for non-existent user {user_id}")
                await websocket.close(code=1008, reason="User not found")
                return

            break

        # Accept connection
        await manager.connect(websocket, user_id)
        logger.info(f"✅ WebSocket connected successfully for user {user_id}")

        # Keep connection alive
        while True:
            # Wait for any message from client (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if user_id:
            manager.disconnect(websocket, user_id)
