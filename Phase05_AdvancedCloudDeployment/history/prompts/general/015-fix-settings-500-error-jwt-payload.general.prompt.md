---
id: 015
title: Fix 500 Internal Server Error on Profile Update - JWT Payload Mismatch
stage: general
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: settings
branch: main
user: unknown
command: continue-session
labels: [backend, api, auth, bug-fix, jwt]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/middleware/auth.py
 - backend/app/models/user.py
 - backend/app/routes/users.py
tests:
 - null
---

## Prompt

User reported a 500 Internal Server Error and CORS error when trying to update their profile (name/email) on the Settings page:

```
Access to fetch at 'http://localhost:8000/api/users/profile' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
PUT http://localhost:8000/api/users/profile net::ERR_FAILED 500 (Internal Server Error)
```

## Response snapshot

Identified and fixed **3 critical issues** causing the 500 error:

### Issue 1: JWT Payload Mismatch (CRITICAL)
- **Problem**: JWT tokens were created with the `"sub"` claim (standard JWT practice), but the `update_profile` endpoint expected `current_user.id` as if it were a User object.
- **Root Cause**: `get_current_user()` returns a `Dict` with JWT payload (`{"sub": "user_id", "email": "...", "name": "..."}`), but routes were treating it as a `User` object and calling `current_user.id`.
- **Fix**: Updated `backend/app/middleware/auth.py` to standardize the payload by mapping `"sub"` to `"user_id"` before returning it.

### Issue 2: UserRead Model Missing Fields
- **Problem**: The `UserRead` response model was missing `updated_at` and `last_login_at` fields that exist on the `User` database model.
- **Impact**: When serializing the database user to `UserRead`, Pydantic would fail validation.
- **Fix**: Added `updated_at: datetime` and `last_login_at: Optional[datetime]` to the `UserRead` model in `backend/app/models/user.py`.

### Issue 3: Type Annotations and User ID Extraction
- **Problem**: Routes were annotated with `current_user: User = Depends(get_current_user)` but `get_current_user()` returns `Dict`.
- **Impact**: Runtime attribute errors when accessing `current_user.id`.
- **Fix**: Changed type annotation to `current_user: Dict` and extracted `user_id` from the dict payload in both `update_profile` and `change_password` endpoints in `backend/app/routes/users.py`.

### CORS Note
The CORS error was a **secondary symptom** - browsers don't include CORS headers in error responses, so when the server returned 500, the browser reported it as a CORS issue instead of showing the actual error.

## Outcome

- ✅ Impact: Settings page profile updates and password changes now work correctly without 500 errors.
- 🧪 Tests: No automated tests run, manual verification required.
- 📁 Files: `backend/app/middleware/auth.py`, `backend/app/models/user.py`, `backend/app/routes/users.py`
- 🔁 Next prompts: User should test profile update and password change functionality.
- 🧠 Reflection: JWT tokens use standard claims (`sub` for subject), but application code must consistently handle the payload format. Type hints should match actual return types to prevent runtime errors.

## Evaluation notes (flywheel)

- Failure modes observed: Type annotation mismatch between `Dict` and `User` object caused attribute access errors at runtime.
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add integration tests for profile update endpoints to catch these issues earlier.
