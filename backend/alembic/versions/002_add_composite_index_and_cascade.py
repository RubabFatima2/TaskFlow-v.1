"""Add composite index and verify CASCADE delete

Revision ID: 002
Revises: 001
Create Date: 2026-04-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add composite index for optimized queries (user_id, completed, created_at)
    op.create_index(
        'ix_tasks_user_completed_created',
        'tasks',
        ['user_id', 'completed', 'created_at'],
        unique=False
    )

    # Verify CASCADE delete is set (already in 001, but ensuring it's correct)
    # Drop and recreate foreign key with explicit CASCADE
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(
        'tasks_user_id_fkey',
        'tasks',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove composite index
    op.drop_index('ix_tasks_user_completed_created', table_name='tasks')

    # Restore original foreign key without CASCADE
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(
        'tasks_user_id_fkey',
        'tasks',
        'users',
        ['user_id'],
        ['id']
    )
