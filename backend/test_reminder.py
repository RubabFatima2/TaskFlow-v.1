"""
Test script to verify reminder service is working
Creates a test task with a reminder 2 minutes from now
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.task import Task
from app.services.reminder_service import reminder_service

async def test_reminder():
    print("Testing reminder service...")

    # Create a test task with reminder 2 minutes from now
    async for session in get_session():
        # Check if reminder service is running
        print(f"Reminder service notification manager: {reminder_service.notification_manager}")

        # Create test task
        now = datetime.utcnow()
        due_time = now + timedelta(minutes=2)

        test_task = Task(
            user_id=1,  # Replace with actual user ID
            title="Test Reminder Task",
            description="This task should trigger a reminder in 2 minutes",
            priority="high",
            due_date=due_time,
            reminder_enabled=True,
            reminder_minutes_before=1,  # Remind 1 minute before due date
            completed=False
        )

        session.add(test_task)
        await session.commit()
        await session.refresh(test_task)

        print(f"✅ Created test task ID: {test_task.id}")
        print(f"   Due date: {test_task.due_date}")
        print(f"   Reminder will trigger at: {test_task.due_date - timedelta(minutes=1)}")
        print(f"   Current time: {now}")
        print(f"\nWait 1 minute and check for reminder notification...")

        break

if __name__ == "__main__":
    asyncio.run(test_reminder())
