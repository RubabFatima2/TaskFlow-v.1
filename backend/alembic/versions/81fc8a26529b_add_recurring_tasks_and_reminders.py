# Mako template for Alembic migration script
"""add_recurring_tasks_and_reminders

Revision ID: 81fc8a26529b
Revises: d2cb10f2d72b
Create Date: 2026-04-22 15:13:00.840182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81fc8a26529b'
down_revision = 'd2cb10f2d72b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change due_date from Date to DateTime
    op.alter_column('tasks', 'due_date',
                    type_=sa.DateTime(),
                    existing_type=sa.Date(),
                    nullable=True)

    # Add recurring task fields
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(length=50), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_interval', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.Date(), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Add reminder fields
    op.add_column('tasks', sa.Column('reminder_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('reminder_minutes_before', sa.Integer(), nullable=True))

    # Create index for recurring tasks
    op.create_index('ix_tasks_recurring', 'tasks', ['is_recurring'], unique=False)


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_tasks_recurring', table_name='tasks')

    # Drop reminder fields
    op.drop_column('tasks', 'reminder_minutes_before')
    op.drop_column('tasks', 'reminder_enabled')

    # Drop recurring task fields
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')

    # Change due_date back from DateTime to Date
    op.alter_column('tasks', 'due_date',
                    type_=sa.Date(),
                    existing_type=sa.DateTime(),
                    nullable=True)
