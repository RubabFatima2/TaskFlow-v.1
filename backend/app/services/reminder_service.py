import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.task import Task
from app.database import get_session
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for checking and triggering task reminders"""

    def __init__(self):
        self.notification_manager = None

    def set_notification_manager(self, manager):
        """Set the WebSocket connection manager for sending notifications"""
        self.notification_manager = manager

    async def check_reminders(self, session: AsyncSession) -> list[Task]:
        """Check for tasks that need reminders sent"""
        now = datetime.now(timezone.utc)

        # Find tasks with reminders enabled, not completed, with due dates
        query = select(Task).where(
            Task.reminder_enabled == True,
            Task.completed == False,
            Task.due_date.isnot(None)
        )

        result = await session.execute(query)
        tasks = result.scalars().all()

        tasks_to_remind = []
        for task in tasks:
            if task.due_date and task.reminder_minutes_before:
                # Calculate when reminder should be sent
                reminder_time = task.due_date - timedelta(minutes=task.reminder_minutes_before)

                # Check if we're within 1 minute of reminder time (to avoid missing it)
                time_diff = abs((now - reminder_time).total_seconds())

                if time_diff <= 60:  # Within 1 minute window
                    tasks_to_remind.append(task)
                    logger.info(f"Reminder triggered for task {task.id}: {task.title}")

                    # Send WebSocket notification if manager is available
                    if self.notification_manager:
                        await self.notification_manager.send_notification(
                            task.user_id,
                            {
                                "type": "task_reminder",
                                "task_id": task.id,
                                "title": task.title,
                                "description": task.description,
                                "due_date": task.due_date.isoformat(),
                                "priority": task.priority
                            }
                        )

        return tasks_to_remind

    async def run_reminder_loop(self):
        """Background loop that checks for reminders every minute"""
        logger.info("Reminder service started")

        while True:
            try:
                async for session in get_session():
                    tasks = await self.check_reminders(session)

                    if tasks:
                        logger.info(f"Found {len(tasks)} tasks needing reminders")

                    break  # Exit the async for loop after one iteration

            except Exception as e:
                logger.error(f"Error in reminder loop: {e}")

            # Wait 1 minute before next check
            await asyncio.sleep(60)


# Global instance
reminder_service = ReminderService()
