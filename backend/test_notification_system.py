"""
Comprehensive test for reminder notification system
Run this while the backend server is running
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.task import Task
from app.services.reminder_service import reminder_service
from sqlmodel import select

async def test_notification_system():
    print("=" * 60)
    print("REMINDER NOTIFICATION SYSTEM TEST")
    print("=" * 60)

    async for session in get_session():
        # 1. Check if reminder service has notification manager
        print("\n1. Checking Reminder Service Setup:")
        print(f"   Notification Manager: {reminder_service.notification_manager}")
        if reminder_service.notification_manager:
            print(f"   Active Connections: {reminder_service.notification_manager.active_connections}")
        else:
            print("   ❌ WARNING: Notification manager not set!")

        # 2. Check existing tasks with reminders
        print("\n2. Checking Existing Tasks with Reminders:")
        query = select(Task).where(
            Task.reminder_enabled == True,
            Task.completed == False,
            Task.due_date.isnot(None)
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        if tasks:
            print(f"   Found {len(tasks)} tasks with reminders enabled:")
            for task in tasks:
                print(f"\n   Task ID: {task.id}")
                print(f"   Title: {task.title}")
                print(f"   User ID: {task.user_id}")
                print(f"   Due Date: {task.due_date}")
                print(f"   Reminder Minutes Before: {task.reminder_minutes_before}")
                if task.due_date and task.reminder_minutes_before:
                    reminder_time = task.due_date - timedelta(minutes=task.reminder_minutes_before)
                    now = datetime.utcnow()
                    time_until_reminder = (reminder_time - now).total_seconds()
                    print(f"   Reminder Time: {reminder_time}")
                    print(f"   Current Time: {now}")
                    print(f"   Time Until Reminder: {time_until_reminder:.0f} seconds ({time_until_reminder/60:.1f} minutes)")
        else:
            print("   ❌ No tasks with reminders found!")

        # 3. Create a test task that will trigger in 2 minutes
        print("\n3. Creating Test Task (reminder in 2 minutes):")
        now = datetime.utcnow()
        due_time = now + timedelta(minutes=3)  # Due in 3 minutes

        # Check if user exists
        from app.models.user import User
        user_query = select(User).limit(1)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            print("   ❌ No users found in database!")
            break

        test_task = Task(
            user_id=user.id,
            title=f"TEST REMINDER - {now.strftime('%H:%M:%S')}",
            description="This task should trigger a reminder in 2 minutes",
            priority="high",
            due_date=due_time,
            reminder_enabled=True,
            reminder_minutes_before=1,  # Remind 1 minute before (so 2 minutes from now)
            completed=False
        )

        session.add(test_task)
        await session.commit()
        await session.refresh(test_task)

        reminder_time = due_time - timedelta(minutes=1)
        print(f"   ✅ Created test task ID: {test_task.id}")
        print(f"   User ID: {test_task.user_id}")
        print(f"   Due Date: {due_time}")
        print(f"   Reminder Time: {reminder_time}")
        print(f"   Current Time: {now}")
        print(f"   Reminder will trigger in: ~2 minutes")

        # 4. Test reminder check manually
        print("\n4. Testing Reminder Check Function:")
        tasks_to_remind = await reminder_service.check_reminders(session)
        print(f"   Tasks needing reminders now: {len(tasks_to_remind)}")

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Make sure backend server is running (uvicorn app.main:app --reload)")
        print("2. Make sure frontend is running (npm run dev)")
        print("3. Log in to the application")
        print("4. Open browser console (F12) to check WebSocket connection")
        print("5. Wait 2 minutes for the test reminder to trigger")
        print("6. Check browser notifications (make sure they're allowed)")

        break

if __name__ == "__main__":
    asyncio.run(test_notification_system())
