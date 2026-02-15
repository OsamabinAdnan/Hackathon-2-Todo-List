import sys
import os
sys.path.insert(0, os.getcwd())

from sqlmodel import Session, text
from app.database import engine

def check_database_migration():
    with Session(engine) as session:
        # Check the column types in the database
        print('Checking column types in database:')

        # Check conversations table
        conv_query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'conversations' AND column_name = 'user_id'
        """
        conv_cols = session.exec(text(conv_query)).all()
        print(f'Conversations user_id: {conv_cols}')

        # Check messages table
        msg_query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'messages' AND column_name = 'user_id'
        """
        msg_cols = session.exec(text(msg_query)).all()
        print(f'Messages user_id: {msg_cols}')

        # Check foreign key constraints
        fk_query = """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND (tc.table_name = 'conversations' OR tc.table_name = 'messages')
              AND (kcu.column_name = 'user_id')
        """
        fk_check = session.exec(text(fk_query)).all()
        print(f'Foreign key constraints: {fk_check}')

        # Check a few sample records to confirm they are in UUID format
        conv_sample = session.exec(text('SELECT id, user_id FROM conversations LIMIT 3;')).all()
        print(f'Conversation samples: {conv_sample}')

        msg_sample = session.exec(text('SELECT id, user_id FROM messages LIMIT 3;')).all()
        print(f'Message samples: {msg_sample}')

        print('\nMigration verification completed!')

if __name__ == "__main__":
    check_database_migration()