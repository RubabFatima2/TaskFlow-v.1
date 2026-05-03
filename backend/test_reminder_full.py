"""
Test reminder service by creating a task with a reminder
"""
import asyncio
import httpx
import websockets
import json
from datetime import datetime, timedelta

async def test_reminder_system():
    """Test the complete reminder notification flow"""

    print("=== Testing Reminder & Notification System ===\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("1. Logging in...")
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!"
            }
        )

        if login_response.status_code != 200:
            print(f"[ERROR] Login failed: {login_response.text}")
            return

        access_token = login_response.cookies.get("access_token")
        print(f"[OK] Logged in successfully\n")

        # 2. Create a task with reminder (due in 3 minutes, remind 2 minutes before)
        print("2. Creating task with reminder...")
        due_date = datetime.utcnow() + timedelta(minutes=3)

        task_data = {
            "title": "Test Reminder Task",
            "description": "This task should trigger a reminder notification",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "reminder_enabled": True,
            "reminder_minutes_before": 2  # Remind 2 minutes before due date (so in ~1 minute)
        }

        create_response = await client.post(
            "http://localhost:8000/api/v1/tasks",
            json=task_data,
            cookies={"access_token": access_token}
        )

        if create_response.status_code != 201:
            print(f"[ERROR] Failed to create task: {create_response.text}")
            return

        task = create_response.json()
        print(f"[OK] Task created: ID={task['id']}, Title='{task['title']}'")
        print(f"     Due date: {task['due_date']}")
        print(f"     Reminder: {task['reminder_minutes_before']} minutes before")
        print(f"     Reminder should trigger at: {(due_date - timedelta(minutes=2)).strftime('%H:%M:%S')}")
        print(f"     Current time: {datetime.utcnow().strftime('%H:%M:%S')}\n")

        # 3. Connect to WebSocket and wait for notification
        print("3. Connecting to WebSocket and waiting for reminder notification...")
        print("   (This will wait up to 90 seconds for the notification)\n")

        ws_url = f"ws://localhost:8000/api/v1/notifications/ws?token={access_token}"

        try:
            async with websockets.connect(ws_url) as websocket:
                print("[OK] WebSocket connected\n")

                # Wait for notification (90 seconds max)
                start_time = datetime.utcnow()
                notification_received = False

                while (datetime.utcnow() - start_time).total_seconds() < 90:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)

                        if message == "pong":
                            continue

                        # Got a notification!
                        print(f"[NOTIFICATION RECEIVED] at {datetime.utcnow().strftime('%H:%M:%S')}")
                        print(f"Raw message: {message}\n")

                        notification = json.loads(message)
                        print("Notification details:")
                        print(f"  Type: {notification.get('type')}")
                        print(f"  Task ID: {notification.get('task_id')}")
                        print(f"  Title: {notification.get('title')}")
                        print(f"  Description: {notification.get('description')}")
                        print(f"  Due date: {notification.get('due_date')}")
                        print(f"  Priority: {notification.get('priority')}")

                        notification_received = True
                        break

                    except asyncio.TimeoutError:
                        # Print progress every 5 seconds
                        elapsed = int((datetime.utcnow() - start_time).total_seconds())
                        print(f"[INFO] Waiting... ({elapsed}s elapsed)")

                        # Send ping to keep connection alive
                        await websocket.send("ping")

                if not notification_received:
                    print("\n[WARNING] No notification received within 90 seconds")
                    print("This could mean:")
                    print("  - Reminder service is not running")
                    print("  - Reminder timing window was missed")
                    print("  - WebSocket connection issue")
                else:
                    print("\n[SUCCESS] Reminder notification system is working correctly!")

        except Exception as e:
            print(f"[ERROR] WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_reminder_system())
