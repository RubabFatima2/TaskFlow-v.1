"""
Test WebSocket connection and notification system
"""
import asyncio
import websockets
import json
from datetime import datetime, timedelta

async def test_websocket():
    """Test WebSocket connection with authentication"""

    # First, login to get access token
    import httpx

    print("1. Logging in to get access token...")
    async with httpx.AsyncClient() as client:
        # Try to login (you'll need valid credentials)
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!"
            }
        )

        if login_response.status_code != 200:
            print(f"[ERROR] Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return

        # Extract access token from cookies
        cookies = login_response.cookies
        access_token = cookies.get("access_token")

        if not access_token:
            print("[ERROR] No access token in response")
            return

        print(f"[OK] Login successful, got access token")

        # Test WebSocket connection
        print("\n2. Connecting to WebSocket...")
        ws_url = f"ws://localhost:8000/api/v1/notifications/ws?token={access_token}"

        try:
            async with websockets.connect(ws_url) as websocket:
                print("[OK] WebSocket connected successfully!")

                # Send ping
                print("\n3. Sending ping...")
                await websocket.send("ping")

                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"[OK] Received: {response}")

                # Wait for notifications (10 seconds)
                print("\n4. Waiting for notifications (10 seconds)...")
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        if message != "pong":
                            print(f"[NOTIFICATION] Received: {message}")
                            notification = json.loads(message)
                            print(f"   Type: {notification.get('type')}")
                            print(f"   Task: {notification.get('title')}")
                except asyncio.TimeoutError:
                    print("[INFO] No notifications received in 10 seconds")

        except websockets.exceptions.WebSocketException as e:
            print(f"[ERROR] WebSocket error: {e}")
        except Exception as e:
            print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
