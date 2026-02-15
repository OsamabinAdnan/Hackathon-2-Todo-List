"""Add conversation tables

Revision ID: 20260116_add_conversation_tables
Revises: None
Create Date: 2026-01-16 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
import uuid
from datetime import datetime


# Revision identifiers
revision = '20260116_add_conversation_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_conversations_user_id', 'user_id')
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('conversation_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_messages_user_id', 'user_id'),
        sa.Index('ix_messages_conversation_id', 'conversation_id'),
        sa.Index('ix_messages_created_at', 'created_at')
    )


def downgrade():
    # Drop messages table first (due to foreign key constraint)
    op.drop_table('messages')

    # Drop conversations table
    op.drop_table('conversations')