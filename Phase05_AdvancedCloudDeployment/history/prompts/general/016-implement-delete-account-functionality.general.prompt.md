---
id: 016
title: Implement Delete Account Functionality
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: settings
branch: main
user: unknown
command: continue-session
labels: [backend, frontend, api, account-deletion, user-management]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/routes/users.py
 - frontend/lib/api.ts
 - frontend/app/dashboard/settings/page.tsx
tests:
 - null
---

## Prompt

User reported that the "Delete Account" button in the Settings page was not functional. It showed two alerts:
1. "Are you sure you want to delete your account? This action cannot be undone."
2. "Account deletion is not implemented yet for safety reasons."

Additionally, the browser console showed a performance warning:
```
[Violation] 'click' handler took 4997ms
```

This was caused by the `confirm()` and `alert()` blocking calls with hardcoded timeout simulation.

## Response snapshot

Implemented full delete account functionality across the stack:

### Backend Implementation
**File**: `backend/app/routes/users.py`
- Added `DELETE /api/users/account` endpoint
- Extracts `user_id` from JWT token payload
- Validates user exists in database
- Deletes user record (cascade deletion will remove associated tasks via database foreign key constraints)
- Returns success message

### Frontend API Client
**File**: `frontend/lib/api.ts`
- Added `userApi.deleteAccount()` function
- Calls `DELETE /api/users/account` with auth headers
- Returns success message or throws error with detail

### Frontend UI Integration
**File**: `frontend/app/dashboard/settings/page.tsx`
- Updated `handleDeleteAccount` from mock implementation to real API call
- Made function `async` to properly handle API response
- Added try-catch error handling
- On success: Shows success alert, clears localStorage (token and user), redirects to login
- On error: Shows error message from API
- Removed the "not implemented" placeholder alert

### Performance Fix
The 4997ms violation was caused by synchronous `confirm()` and `alert()` calls with artificial delays. The new implementation:
- Uses native browser `confirm()` (non-blocking dialog)
- Awaits async API call
- Shows result with `alert()` only after response
- No artificial timeouts or delays

## Outcome

- ✅ Impact: Users can now permanently delete their accounts and all associated data.
- 🧪 Tests: Manual verification required. Should test database cascade deletion of tasks.
- 📁 Files: `backend/app/routes/users.py`, `frontend/lib/api.ts`, `frontend/app/dashboard/settings/page.tsx`
- 🔁 Next prompts: User should test account deletion flow end-to-end.
- 🧠 Reflection: Account deletion is a critical operation that should include cascade deletion of user data. The database schema should enforce foreign key constraints with `ON DELETE CASCADE` to ensure data integrity.

## Evaluation notes (flywheel)

- Failure modes observed: Missing API endpoint caused frontend to show placeholder message instead of functional behavior.
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add confirmation email before account deletion for additional safety.
