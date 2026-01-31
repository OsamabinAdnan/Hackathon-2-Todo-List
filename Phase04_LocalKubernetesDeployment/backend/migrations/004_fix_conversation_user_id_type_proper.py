"""
Migration script to fix conversation and message table user_id column types.
This script properly handles the conversion from VARCHAR to UUID in the database.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, text, select
from app.database import engine
from app.models.conversation import Conversation, Message
from app.models.user import User
import uuid

def run_migration():
    """Execute the proper user_id type conversion migration."""
    print("[*] Starting migration: Fix conversation and message user_id column types to UUID...")

    try:
        with Session(engine) as session:
            print("  [1/4] Dropping foreign key constraints...")

            # Drop foreign key constraints first to allow column modification
            try:
                session.exec(text("ALTER TABLE conversations DROP CONSTRAINT IF EXISTS fk_conversations_user_id;"))
                session.exec(text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS fk_messages_user_id;"))
                print("    - Dropped foreign key constraints successfully")
            except Exception as e:
                print(f"    - Warning: Could not drop foreign key constraints: {e}")

            print("  [2/4] Updating data to ensure proper UUID format...")

            # First, let's check the current format of user_id values in conversations and messages
            # We'll update any string-formatted UUIDs to proper UUID format
            try:
                # Update conversations table - convert string UUIDs to proper format
                # This will ensure that string representations of UUIDs are properly formatted
                conv_results = session.exec(text("SELECT DISTINCT user_id FROM conversations;")).all()

                for row in conv_results:
                    user_id_str = str(row[0])  # This gets the string representation
                    try:
                        # Try to parse it as UUID to normalize it
                        normalized_uuid = str(uuid.UUID(user_id_str))
                        # Update the value if it was in a different format
                        session.exec(
                            text("UPDATE conversations SET user_id = :normalized_uuid WHERE user_id = :original"),
                            {"normalized_uuid": normalized_uuid, "original": user_id_str}
                        )
                    except ValueError:
                        print(f"    - Warning: Invalid UUID format found: {user_id_str}")

                print("    - Normalized conversation user_id values")
            except Exception as e:
                print(f"    - Warning: Could not normalize conversation user_id values: {e}")

            try:
                # Update messages table - convert string UUIDs to proper format
                msg_results = session.exec(text("SELECT DISTINCT user_id FROM messages;")).all()

                for row in msg_results:
                    user_id_str = str(row[0])  # This gets the string representation
                    try:
                        # Try to parse it as UUID to normalize it
                        normalized_uuid = str(uuid.UUID(user_id_str))
                        # Update the value if it was in a different format
                        session.exec(
                            text("UPDATE messages SET user_id = :normalized_uuid WHERE user_id = :original"),
                            {"normalized_uuid": normalized_uuid, "original": user_id_str}
                        )
                    except ValueError:
                        print(f"    - Warning: Invalid UUID format found: {user_id_str}")

                print("    - Normalized message user_id values")
            except Exception as e:
                print(f"    - Warning: Could not normalize message user_id values: {e}")

            print("  [3/4] Changing column types to UUID...")

            # Now change the column types to UUID
            # For PostgreSQL, we need to ensure the data is in proper UUID format first
            try:
                # Change conversations.user_id to UUID type
                session.exec(text("ALTER TABLE conversations ALTER COLUMN user_id TYPE UUID USING user_id::UUID;"))
                print("    - Changed conversations.user_id to UUID type")
            except Exception as e:
                print(f"    - Warning: Could not change conversations.user_id type: {e}")

            try:
                # Change messages.user_id to UUID type
                session.exec(text("ALTER TABLE messages ALTER COLUMN user_id TYPE UUID USING user_id::UUID;"))
                print("    - Changed messages.user_id to UUID type")
            except Exception as e:
                print(f"    - Warning: Could not change messages.user_id type: {e}")

            print("  [4/4] Recreating foreign key constraints...")

            # Recreate foreign key constraints
            try:
                session.exec(text(
                    "ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user_id "
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"
                ))
                session.exec(text(
                    "ALTER TABLE messages ADD CONSTRAINT fk_messages_user_id "
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"
                ))
                print("    - Recreated foreign key constraints successfully")
            except Exception as e:
                print(f"    - Warning: Could not recreate foreign key constraints: {e}")

            session.commit()
            print("\n[SUCCESS] Conversation and message user_id columns updated to UUID type successfully!")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise


def validate_migration():
    """Validate that the migration was applied correctly."""
    print("[*] Validating migration...")

    try:
        with Session(engine) as session:
            # Check if we can query the tables without foreign key constraint errors
            conv_count = session.exec(text("SELECT COUNT(*) FROM conversations;")).one()[0]
            msg_count = session.exec(text("SELECT COUNT(*) FROM messages;")).one()[0]

            print(f"    - Found {conv_count} conversations")
            print(f"    - Found {msg_count} messages")

            # Check column types in information_schema
            col_info_conv = session.exec(text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'conversations' AND column_name = 'user_id';
            """)).all()

            col_info_msg = session.exec(text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'messages' AND column_name = 'user_id';
            """)).all()

            if col_info_conv and col_info_msg:
                conv_type = col_info_conv[0][0] if col_info_conv else "unknown"
                msg_type = col_info_msg[0][0] if col_info_msg else "unknown"

                print(f"    - conversations.user_id type: {conv_type}")
                print(f"    - messages.user_id type: {msg_type}")

                if conv_type.lower() == 'uuid' and msg_type.lower() == 'uuid':
                    print("\n[SUCCESS] Both user_id columns are now of UUID type!")
                    return True
                else:
                    print("\n[WARNING] Column types may not be properly set to UUID")
                    return False
            else:
                print("\n[ERROR] Could not verify column types")
                return False

    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Database Migration: Fix Conversation User_ID Column Types to UUID")
    print("=" * 70)
    print()

    # Check for --yes flag for non-interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Running in non-interactive mode (--yes flag provided)")
        run_migration()
        validate_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == '--validate':
        print("Running validation only")
        validate_migration()
    else:
        # Interactive mode - ask for confirmation
        response = input("This will modify the database structure and convert user_id columns to UUID type. Continue? (yes/no): ")

        if response.lower() in ["yes", "y"]:
            run_migration()
            validate_migration()
        else:
            print("Migration cancelled.")