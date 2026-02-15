"""Fix user_id column type to UUID to match users.id

Revision ID: 20260129_fix_user_id_uuid_constraint
Revises: 20260116_add_conversation_tables
Create Date: 2026-01-29 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# Revision identifiers
revision = '20260129_fix_user_id_uuid_constraint'
down_revision = '20260116_add_conversation_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraints first
    op.drop_constraint('messages_user_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')

    # Alter the column types from String to GUID (UUID)
    with op.batch_alter_table('conversations') as batch_op:
        batch_op.alter_column('user_id',
                             existing_type=sa.String(),
                             type_=sqlmodel.sql.sqltypes.GUID(),
                             postgresql_using='user_id::uuid')

    with op.batch_alter_table('messages') as batch_op:
        batch_op.alter_column('user_id',
                             existing_type=sa.String(),
                             type_=sqlmodel.sql.sqltypes.GUID(),
                             postgresql_using='user_id::uuid')

    # Recreate foreign key constraints
    op.create_foreign_key('conversations_user_id_fkey', 'conversations', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('messages_user_id_fkey', 'messages', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Drop foreign key constraints first
    op.drop_constraint('messages_user_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')

    # Revert column types from GUID back to String
    with op.batch_alter_table('conversations') as batch_op:
        batch_op.alter_column('user_id',
                             existing_type=sqlmodel.sql.sqltypes.GUID(),
                             type_=sa.String())

    with op.batch_alter_table('messages') as batch_op:
        batch_op.alter_column('user_id',
                             existing_type=sqlmodel.sql.sqltypes.GUID(),
                             type_=sa.String())

    # Recreate original foreign key constraints
    op.create_foreign_key('conversations_user_id_fkey', 'conversations', 'users', ['user_id'], ['id'])
    op.create_foreign_key('messages_user_id_fkey', 'messages', 'users', ['user_id'], ['id'])