"""
Database migration script for adding email verification support.
Run this script to add email_verified field and mark existing users as verified.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, text
from app.database import engine


def run_migration():
    """Execute the email_verified migration."""
    print("[*] Starting migration: Add email_verified field...")

    try:
        with Session(engine) as session:
            # Read migration SQL file
            migration_file = os.path.join(
                os.path.dirname(__file__),
                "001_add_email_verified.sql"
            )

            with open(migration_file, "r") as f:
                sql_content = f.read()

            # Remove comments and split by semicolon
            lines = [line for line in sql_content.split('\n') if line.strip() and not line.strip().startswith('--')]
            sql_cleaned = '\n'.join(lines)

            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_cleaned.split(";") if s.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    # Show abbreviated statement for logging
                    preview = statement[:70].replace('\n', ' ')
                    if len(statement) > 70:
                        preview += "..."
                    print(f"  [{i}/{len(statements)}] Executing: {preview}")

                    # Execute statement
                    result = session.exec(text(statement))

                    # If it's a SELECT statement, fetch results
                    if statement.strip().upper().startswith('SELECT'):
                        row = result.first()
                        if row:
                            print(f"      -> Result: Total users: {row[0]}, Verified: {row[1]}")

            session.commit()
            print("\n[SUCCESS] Migration completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Email Verification Support")
    print("=" * 60)
    print()

    # Check for --yes flag for non-interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Running in non-interactive mode (--yes flag provided)")
        run_migration()
    else:
        # Interactive mode - ask for confirmation
        response = input("This will modify the database. Continue? (yes/no): ")

        if response.lower() in ["yes", "y"]:
            run_migration()
        else:
            print("Migration cancelled.")
