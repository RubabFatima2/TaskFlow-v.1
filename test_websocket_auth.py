"""Test WebSocket connection with authentication"""
import asyncio
import websockets
import httpx
import json

async def test_websocket_with_auth():
    """Test WebSocket connection with proper authentication"""

    # Step 1: Login to get access token
    print("Step 1: Logging in to get access token...")
    async with httpx.AsyncClient() as client:
        try:
            # Try to login with test credentials
            login_response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"email": "wstest@example.com", "password": "TestPass123!"}
            )

            if login_response.status_code != 200:
                print(f"Login failed with status {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return

            # Extract token from cookies
            cookies = login_response.cookies
            access_token = cookies.get("access_token")

            if not access_token:
                print("No access token in response cookies")
                print(f"Available cookies: {list(cookies.keys())}")
                return

            print(f"Login successful, got access token")

        except Exception as e:
            print(f"Login error: {e}")
            return

    # Step 2: Connect to WebSocket with token
    print("\nStep 2: Connecting to WebSocket...")
    try:
        # Try with token as query parameter
        uri = f"ws://localhost:8000/api/v1/notifications/ws?token={access_token}"
        print(f"Connecting to: {uri[:60]}...")

        async with websockets.connect(uri) as websocket:
            print("WebSocket connected successfully!")

            # Send a ping
            print("\nStep 3: Sending ping...")
            await websocket.send("ping")

            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"Received: {response}")

            print("\nWebSocket is working correctly!")

    except websockets.exceptions.InvalidStatus as e:
        print(f"WebSocket rejected connection: HTTP {e.status_code}")
    except asyncio.TimeoutError:
        print("Timeout waiting for response")
    except Exception as e:
        print(f"WebSocket error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_with_auth())
