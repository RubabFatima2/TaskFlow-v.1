# Mako template for Alembic migration script
"""add_priority_tags_due_date_to_tasks

Revision ID: d2cb10f2d72b
Revises: 003
Create Date: 2026-04-22 15:04:04.433040

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd2cb10f2d72b'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add priority column with default 'medium'
    op.add_column('tasks', sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'))

    # Add tags column as JSON array
    op.add_column('tasks', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add due_date column
    op.add_column('tasks', sa.Column('due_date', sa.Date(), nullable=True))

    # Create indexes for better query performance
    op.create_index('ix_tasks_priority', 'tasks', ['priority'], unique=False)
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tasks_due_date', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
