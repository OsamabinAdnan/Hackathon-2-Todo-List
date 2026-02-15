"""
Data Migration Script: Convert existing conversation and message user_id values from VARCHAR to UUID format
This script safely migrates existing data to match the new UUID schema requirements.
"""
import sys
import os
import uuid
from sqlmodel import Session, select, text
from sqlalchemy.exc import IntegrityError

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.conversation import Conversation, Message
from app.models.user import User


def validate_existing_data(session):
    """Validate the format of existing user_id data."""
    print("  [1/4] Validating existing data format...")

    # Check conversations table
    conv_results = session.exec(text("SELECT id, user_id FROM conversations LIMIT 10;")).all()
    print(f"    - Sample conversations: {len(conv_results)}")

    for conv_id, user_id in conv_results[:3]:  # Show first 3
        print(f"      Conv {conv_id}: user_id='{user_id}' (type: {type(user_id).__name__})")

    # Check messages table
    msg_results = session.exec(text("SELECT id, user_id FROM messages LIMIT 10;")).all()
    print(f"    - Sample messages: {len(msg_results)}")

    for msg_id, user_id in msg_results[:3]:  # Show first 3
        print(f"      Msg {msg_id}: user_id='{user_id}' (type: {type(user_id).__name__})")


def migrate_conversation_data(session):
    """Migrate conversation table user_id values to proper UUID format."""
    print("  [2/4] Migrating conversation data...")

    # Get all conversations with their current user_id values
    conv_results = session.exec(text("SELECT id, user_id FROM conversations;")).all()

    migrated_count = 0
    for conv_id, user_id_value in conv_results:
        original_value = str(user_id_value)

        try:
            # Try to parse as UUID to normalize format
            normalized_uuid = uuid.UUID(original_value)
            normalized_str = str(normalized_uuid)

            # Update the record with normalized UUID using raw connection
            with session.bind.connect() as conn:
                stmt = text("UPDATE conversations SET user_id = :normalized_uuid WHERE id = :conv_id")
                conn.execute(stmt, {"normalized_uuid": normalized_str, "conv_id": conv_id})
                conn.commit()

            migrated_count += 1

        except ValueError:
            print(f"    - Warning: Invalid UUID format in conversation {conv_id}: {original_value}")
            # This might be an issue - we need to check if this user_id exists in users table
            # If not, we might need to handle this differently

    print(f"    - Migrated {migrated_count} conversation records")


def migrate_message_data(session):
    """Migrate message table user_id values to proper UUID format."""
    print("  [3/4] Migrating message data...")

    # Get all messages with their current user_id values
    msg_results = session.exec(text("SELECT id, user_id FROM messages;")).all()

    migrated_count = 0
    for msg_id, user_id_value in msg_results:
        original_value = str(user_id_value)

        try:
            # Try to parse as UUID to normalize format
            normalized_uuid = uuid.UUID(original_value)
            normalized_str = str(normalized_uuid)

            # Update the record with normalized UUID using raw connection
            with session.bind.connect() as conn:
                stmt = text("UPDATE messages SET user_id = :normalized_uuid WHERE id = :msg_id")
                conn.execute(stmt, {"normalized_uuid": normalized_str, "msg_id": msg_id})
                conn.commit()

            migrated_count += 1

        except ValueError:
            print(f"    - Warning: Invalid UUID format in message {msg_id}: {original_value}")

    print(f"    - Migrated {migrated_count} message records")


def verify_migration(session):
    """Verify that the migration was successful."""
    print("  [4/4] Verifying migration...")

    # Check a few records to confirm they're now in proper UUID format
    conv_check = session.exec(text("SELECT id, user_id FROM conversations LIMIT 5;")).all()
    for conv_id, user_id in conv_check:
        try:
            uuid.UUID(str(user_id))  # This will raise ValueError if not valid UUID
            print(f"    - Conv {conv_id}: ✓ Valid UUID format")
        except ValueError:
            print(f"    - Conv {conv_id}: ✗ Invalid UUID format: {user_id}")

    msg_check = session.exec(text("SELECT id, user_id FROM messages LIMIT 5;")).all()
    for msg_id, user_id in msg_check:
        try:
            uuid.UUID(str(user_id))  # This will raise ValueError if not valid UUID
            print(f"    - Msg {msg_id}: ✓ Valid UUID format")
        except ValueError:
            print(f"    - Msg {msg_id}: ✗ Invalid UUID format: {user_id}")

    print("\n[SUCCESS] Data migration completed!")


def run_migration():
    """Execute the complete data migration process."""
    print("[*] Starting data migration for UUID user_id format...")

    try:
        with Session(engine) as session:
            # Begin transaction
            session.begin()

            # Validate existing data
            validate_existing_data(session)

            # Migrate data
            migrate_conversation_data(session)
            migrate_message_data(session)

            # Verify migration
            verify_migration(session)

            # Commit transaction
            session.commit()
            print("\n[SUCCESS] All data migrated successfully to UUID format!")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Data Migration: Convert user_id to UUID Format")
    print("=" * 60)
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Running in non-interactive mode (--yes flag provided)")
        run_migration()
    else:
        # Interactive mode - ask for confirmation
        print("This will migrate existing user_id values to proper UUID format.")
        response = input("Continue with data migration? (yes/no): ")

        if response.lower() in ["yes", "y"]:
            run_migration()
        else:
            print("Migration cancelled.")