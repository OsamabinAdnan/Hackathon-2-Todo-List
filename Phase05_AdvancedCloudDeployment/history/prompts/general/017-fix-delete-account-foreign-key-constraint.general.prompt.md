---
id: 017
title: Fix Delete Account Foreign Key Constraint Violation
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: settings
branch: main
user: unknown
command: continue-session
labels: [backend, database, foreign-key, bug-fix]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/routes/users.py
tests:
 - null
---

## Prompt

User reported a 500 Internal Server Error and CORS error when trying to delete their account. Backend logs showed a foreign key constraint violation:

```
psycopg2.errors.ForeignKeyViolation: update or delete on table "users" violates foreign key constraint "tasks_user_id_fkey" on table "tasks"
DETAIL:  Key (id)=(827b230c-79a3-4611-9399-27b8dc783aa4) is still referenced from table "tasks".
```

The database was preventing the user deletion because the user still had tasks associated with their account, and the foreign key constraint was blocking the cascade deletion.

## Response snapshot

### Root Cause
The database foreign key constraint `tasks_user_id_fkey` on the `tasks` table references the `users` table. When trying to delete a user who has tasks, PostgreSQL enforces referential integrity and blocks the deletion unless:
1. The foreign key is defined with `ON DELETE CASCADE` (not set in current schema), OR
2. The application explicitly deletes child records (tasks) before deleting the parent record (user)

### Fix Applied
Updated `backend/app/routes/users.py` in the `delete_account` endpoint:
1. Import the `Task` model
2. Query all tasks belonging to the user: `session.exec(select(Task).where(Task.user_id == user_id)).all()`
3. Iterate through tasks and delete each one: `session.delete(task)`
4. After all tasks are deleted, delete the user: `session.delete(db_user)`
5. Commit the transaction

This ensures tasks are deleted BEFORE the user, preventing the foreign key violation.

### Alternative Solution (Not Implemented)
Could modify the database schema to add `ON DELETE CASCADE` to the foreign key constraint:
```sql
ALTER TABLE tasks
DROP CONSTRAINT tasks_user_id_fkey,
ADD CONSTRAINT tasks_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES users(id)
  ON DELETE CASCADE;
```

However, explicit deletion in application code is more transparent and allows for future enhancements like soft deletes, audit logs, or data backups before deletion.

## Outcome

- ✅ Impact: Users can now successfully delete their accounts along with all their tasks.
- 🧪 Tests: Manual verification required. Should test with users who have multiple tasks.
- 📁 Files: `backend/app/routes/users.py`
- 🔁 Next prompts: User should restart backend and test account deletion.
- 🧠 Reflection: Foreign key constraints enforce data integrity but require careful ordering of deletions. Application-level cascade deletion provides more control than database-level CASCADE constraints.

## Evaluation notes (flywheel)

- Failure modes observed: Forgot to delete child records (tasks) before parent record (user), causing database constraint violation.
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Consider adding a soft delete feature (mark as deleted instead of hard delete) for data recovery purposes.
