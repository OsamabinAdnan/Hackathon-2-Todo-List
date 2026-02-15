"""
Database migration script to fix table structure inconsistencies.
This migration addresses:
1. Tasks table: Remove redundant 'completed' column (status field should handle this)
2. Tasks table: Remove redundant 'user' column (user_id should be sufficient)
3. Tasks table: Remove redundant 'is_recurring' column (recurrence_pattern should handle this)
4. Messages table: Remove 'role' duplicate and 'tool_response'/'tool_responses' columns
5. Conversations table: Remove extra columns
6. Users table: Remove extra columns
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, text
from app.database import engine


def run_migration():
    """Execute the table structure fix migration."""
    print("[*] Starting migration: Fix table structure inconsistencies...")

    try:
        with Session(engine) as session:
            print("  [1/5] Fixing tasks table - removing redundant columns...")

            # Check if 'completed' column exists and remove it (status field should handle completion status)
            try:
                session.exec(text("ALTER TABLE tasks DROP COLUMN IF EXISTS completed;"))
                print("    - Removed 'completed' column (handled by 'status' field)")
            except Exception as e:
                print(f"    - Warning: Could not drop 'completed' column: {e}")

            # Check if 'user' column exists and remove it (user_id is sufficient)
            try:
                session.exec(text("ALTER TABLE tasks DROP COLUMN IF EXISTS \"user\";"))
                print("    - Removed 'user' column (redundant with 'user_id')")
            except Exception as e:
                print(f"    - Warning: Could not drop 'user' column: {e}")

            # Check if 'is_recurring' column exists and remove it (recurrence_pattern handles this)
            try:
                session.exec(text("ALTER TABLE tasks DROP COLUMN IF EXISTS is_recurring;"))
                print("    - Removed 'is_recurring' column (redundant with 'recurrence_pattern')")
            except Exception as e:
                print(f"    - Warning: Could not drop 'is_recurring' column: {e}")

            print("  [2/5] Fixing messages table - removing duplicate columns...")

            # Check if duplicate 'role' column exists
            try:
                session.exec(text("ALTER TABLE messages DROP COLUMN IF EXISTS role_duplicate;"))
                print("    - Removed duplicate 'role' column if it exists")
            except Exception as e:
                print(f"    - Warning: Could not drop duplicate 'role' column: {e}")

            # Check if 'tool_response' column exists (singular form)
            try:
                session.exec(text("ALTER TABLE messages DROP COLUMN IF EXISTS tool_response;"))
                print("    - Removed 'tool_response' column (keeping 'tool_calls' and 'tool_responses')")
            except Exception as e:
                print(f"    - Warning: Could not drop 'tool_response' column: {e}")

            print("  [3/5] Fixing conversations table - removing extra columns...")

            # Remove extra columns that shouldn't exist
            try:
                session.exec(text("ALTER TABLE conversations DROP COLUMN IF EXISTS user_id_user_id;"))
                print("    - Removed 'user_id_user_id' column")
            except Exception as e:
                print(f"    - Warning: Could not drop 'user_id_user_id' column: {e}")

            try:
                session.exec(text("ALTER TABLE conversations DROP COLUMN IF EXISTS id_messages_conversation_id;"))
                print("    - Removed 'id_messages_conversation_id' column")
            except Exception as e:
                print(f"    - Warning: Could not drop 'id_messages_conversation_id' column: {e}")

            print("  [4/5] Fixing users table - removing extra columns...")

            # Remove extra columns that shouldn't exist
            try:
                session.exec(text("ALTER TABLE users DROP COLUMN IF EXISTS id_conversations_user_id;"))
                print("    - Removed 'id_conversations_user_id' column")
            except Exception as e:
                print(f"    - Warning: Could not drop 'id_conversations_user_id' column: {e}")

            try:
                session.exec(text("ALTER TABLE users DROP COLUMN IF EXISTS id_message_user_id;"))
                print("    - Removed 'id_message_user_id' column")
            except Exception as e:
                print(f"    - Warning: Could not drop 'id_message_user_id' column: {e}")

            try:
                session.exec(text("ALTER TABLE users DROP COLUMN IF EXISTS tasks;"))
                print("    - Removed 'tasks' column")
            except Exception as e:
                print(f"    - Warning: Could not drop 'tasks' column: {e}")

            print("  [5/5] Verifying table structure...")

            # Verify that the basic columns still exist
            # Check if tasks table has required columns
            result = session.exec(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name IN ('title', 'status', 'user_id')
            """)).all()

            required_columns = {'title', 'status', 'user_id'}
            found_columns = {row[0] for row in result}

            if required_columns.issubset(found_columns):
                print("    - Tasks table has all required columns")
            else:
                missing = required_columns - found_columns
                print(f"    - Warning: Missing required columns in tasks: {missing}")

            session.commit()
            print("\n[SUCCESS] Table structure inconsistencies fixed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Fix Table Structure Inconsistencies")
    print("=" * 60)
    print()

    # Check for --yes flag for non-interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Running in non-interactive mode (--yes flag provided)")
        run_migration()
    else:
        # Interactive mode - ask for confirmation
        response = input("This will modify the database structure. Continue? (yes/no): ")

        if response.lower() in ["yes", "y"]:
            run_migration()
        else:
            print("Migration cancelled.")