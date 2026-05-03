"""Add updated_at column to users table

Revision ID: 003
Revises: 002
Create Date: 2026-04-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to users table
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column('users', 'updated_at')
