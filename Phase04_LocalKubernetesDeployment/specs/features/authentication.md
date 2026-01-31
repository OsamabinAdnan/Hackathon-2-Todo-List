# Feature: User Authentication & Authorization

**Feature ID**: `authentication`
**Status**: In Progress
**Priority**: Critical (Blocking for all other features)
**Dependencies**: None (Foundation feature)

---

## Overview

Secure multi-user authentication system using Better Auth with JWT tokens. Ensures strict user isolation where users can only access their own tasks.

**Authentication Method**: JWT (JSON Web Token)
**Library**: Better Auth (configured for JWT issuance)
**Token Storage**: HttpOnly cookies (preferred) or localStorage
**Token Expiry**: 7 days
**Password Hashing**: bcrypt or argon2

---

## User Stories

### US-AUTH-1: User Signup
**As a** new visitor
**I want to** create an account
**So that** I can start using the Todo app

**Acceptance Criteria:**
- User provides email, password, and display name
- Email must be unique (no duplicate accounts)
- Password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character (@$!%*?&)
- Display name: 2-50 characters
- Password is hashed before storage (never stored plaintext)
- User account created in database
- User automatically logged in after signup (JWT token issued)
- Welcome email sent (optional, low priority)

**Validation Errors:**
- Email already exists → "An account with this email already exists"
- Invalid email format → "Please enter a valid email address"
- Weak password → "Password must meet requirements: 8+ chars, uppercase, lowercase, number, special char"
- Display name too short/long → "Name must be 2-50 characters"

**Success Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-02T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-01-09T10:30:00Z"
}
```

---

### US-AUTH-2: User Login
**As a** registered user
**I want to** log into my account
**So that** I can access my tasks

**Acceptance Criteria:**
- User provides email and password
- Credentials verified against database (hashed password comparison)
- JWT token issued with user_id, email, expiry
- Token stored in HttpOnly cookie or localStorage
- User redirected to dashboard upon successful login
- Failed login shows generic error (don't reveal if email exists)

**Security Measures:**
- Rate limiting: Max 5 login attempts per 15 minutes per IP
- Generic error message: "Invalid email or password" (don't specify which)
- Account lockout after 10 failed attempts (optional, Phase 3)
- Log failed login attempts (audit trail)

**Success Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-01-09T10:30:00Z"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid email or password"
}
```

---

### US-AUTH-3: User Logout
**As a** logged-in user
**I want to** log out of my account
**So that** I can secure my session

**Acceptance Criteria:**
- User clicks "Logout" button
- JWT token removed from client storage (cookie or localStorage)
- Token invalidated on backend (add to blocklist/revocation list)
- User redirected to login page
- Session data cleared from frontend state

**Backend Token Revocation:**
- Store revoked tokens in Redis or database (expires after 7 days)
- Check token against revocation list on each request
- Return 401 if token is revoked

---

### US-AUTH-4: Persistent Session
**As a** logged-in user
**I want to** remain logged in across browser sessions
**So that** I don't have to log in every time

**Acceptance Criteria:**
- JWT token stored in HttpOnly cookie with 7-day expiry
- User remains logged in until token expires or logout
- Token automatically sent with every API request (Authorization header)
- Frontend checks token validity on app load
- Redirect to login if token expired or invalid

**Token Refresh (Optional, Phase 3):**
- Issue refresh token (30-day expiry) alongside access token
- Access token (7-day expiry) used for API requests
- Refresh token used to obtain new access token when expired

---

### US-AUTH-5: Protected Routes
**As a** system
**I want to** protect all task-related routes
**So that** only authenticated users can access them

**Acceptance Criteria:**
- All `/api/{user_id}/*` routes require valid JWT token
- Frontend redirects to login if no token found
- Backend returns 401 if token invalid/missing
- Backend verifies `user_id` in URL matches `user_id` in token
- Cross-user access blocked (user cannot access other users' tasks)

**Middleware Flow:**
1. Extract `Authorization: Bearer <token>` header
2. Verify JWT signature using `BETTER_AUTH_SECRET`
3. Decode token payload (`user_id`, `email`, `exp`)
4. Check token expiry (`exp` > current time)
5. Check token not in revocation list
6. Compare `user_id` in URL with `user_id` in token
7. If valid → Allow request, attach `user` to request context
8. If invalid → Return 401 Unauthorized

**Unauthorized Response (401):**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

---

### US-AUTH-6: User Profile
**As a** logged-in user
**I want to** view and update my profile
**So that** I can manage my account information

**Acceptance Criteria:**
- User can view current email and display name
- User can update display name (2-50 characters)
- User can change password (requires current password confirmation)
- Email cannot be changed (or requires email verification, Phase 3)
- Profile updates require valid JWT token

**Update Profile Endpoint:**
- `PUT /api/users/profile`
- Request: `{ "name": "New Name" }`
- Response: Updated user object

**Change Password Endpoint:**
- `POST /api/users/change-password`
- Request: `{ "current_password": "...", "new_password": "..." }`
- Validates current password before updating
- Hashes new password before storage

---

## JWT Token Structure

### Token Payload
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1704192600,  // Issued at (Unix timestamp)
  "exp": 1704797400   // Expires at (Unix timestamp, +7 days)
}
```

### Token Generation (Backend)
```python
import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
EXPIRY_DAYS = 7

def create_jwt_token(user_id: str, email: str, name: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=EXPIRY_DAYS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
```

### Token Verification (Backend Middleware)
```python
def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## API Endpoints

See `@specs/api/rest-endpoints.md` for full API documentation.

**Summary:**
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate user, issue JWT token
- `POST /api/auth/logout` - Revoke JWT token
- `GET /api/auth/me` - Get current user info (requires token)
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password

---

## Data Model

### User Entity

```typescript
interface User {
  id: string;                    // UUID, primary key
  email: string;                 // Unique, indexed
  password_hash: string;         // bcrypt/argon2 hash, never exposed in API
  name: string;                  // Display name, 2-50 chars
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  last_login_at: string | null;  // Track last login time
}
```

### Revoked Tokens Table (Optional)
```typescript
interface RevokedToken {
  token_hash: string;            // SHA-256 hash of token (indexed)
  revoked_at: string;            // Timestamp
  expires_at: string;            // Token expiry (for cleanup)
}
```

---

## UI/UX Requirements

### Signup Page (`/signup`)
- **Layout**: Centered card with glassmorphism
- **Fields**:
  - Email (type="email", autocomplete="email")
  - Password (type="password", autocomplete="new-password")
  - Confirm Password (validation: must match)
  - Display Name (type="text", autocomplete="name")
- **Submit Button**: "Create Account" (primary button)
- **Link**: "Already have an account? Log in"
- **Validation**: Real-time validation with inline error messages
- **Loading State**: Spinner + "Creating account..." during API call

### Login Page (`/login`)
- **Layout**: Centered card with glassmorphism
- **Fields**:
  - Email (type="email", autocomplete="email")
  - Password (type="password", autocomplete="current-password")
- **Checkbox**: "Remember me" (extends token expiry, optional)
- **Submit Button**: "Log In" (primary button)
- **Links**:
  - "Forgot password?" (Phase 3)
  - "Don't have an account? Sign up"
- **Error Display**: Generic error banner at top of form

### Profile Page (`/profile`)
- **Header**: User avatar (initials) + name + email
- **Sections**:
  - **Personal Info**: Edit name, view email
  - **Security**: Change password button
  - **Danger Zone**: Delete account (Phase 3)
- **Actions**: "Save Changes", "Cancel"

### Navigation Header (Post-Login)
- **Left**: App logo + "Todo App"
- **Right**: User avatar dropdown
  - Display name
  - Email (gray, smaller)
  - "Profile" menu item
  - "Settings" menu item (Phase 3)
  - Divider
  - "Log Out" (red text)

---

## Security Requirements

### Password Security
- ✅ Passwords hashed with bcrypt (cost factor: 12) or argon2
- ✅ Never store plaintext passwords
- ✅ Never return password_hash in API responses
- ✅ Minimum password strength enforced
- ✅ Disallow common passwords (e.g., "password123")

### Token Security
- ✅ JWT signed with strong secret (BETTER_AUTH_SECRET, 256-bit)
- ✅ Token stored in HttpOnly cookie (XSS protection)
- ✅ Token verified on every protected route
- ✅ Expired tokens rejected
- ✅ Revoked tokens blocked

### User Isolation
- ✅ All API endpoints verify user ownership
- ✅ User A cannot access User B's tasks
- ✅ Database queries filtered by user_id
- ✅ Authorization middleware enforces user_id matching

### Rate Limiting
- ✅ Login: 5 attempts per 15 minutes per IP
- ✅ Signup: 3 accounts per hour per IP
- ✅ Password reset: 3 requests per hour per email (Phase 3)

### Input Validation
- ✅ Email format validation (regex)
- ✅ Password complexity validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (input sanitization, CSP headers)

---

## Error Handling

### Frontend Errors
- Invalid credentials → "Invalid email or password"
- Email already exists → "An account with this email already exists"
- Weak password → "Password does not meet requirements"
- Network error → "Unable to connect. Please try again."
- Token expired → Redirect to login with "Session expired" message

### Backend Errors
- 400 Bad Request: Validation errors (return field-specific messages)
- 401 Unauthorized: Invalid/expired/missing token
- 409 Conflict: Email already exists
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Generic error (log details, don't expose)

---

## Testing Requirements

### Unit Tests
- Password hashing and verification
- JWT token generation and verification
- Token expiry validation
- Password strength validation
- Email format validation

### Integration Tests
- Signup flow → User created in database
- Login flow → Token issued, valid for 7 days
- Logout flow → Token revoked, subsequent requests fail
- Protected route access → 401 without token, 200 with valid token
- Cross-user access attempt → 401 Forbidden

### Security Tests
- Attempt to access User B's tasks with User A's token → 401
- Use expired token → 401
- Use revoked token → 401
- Tamper with token payload → 401 (signature verification fails)
- SQL injection attempt in email field → Rejected
- XSS attempt in name field → Sanitized

### E2E Tests
- User signs up → Redirect to dashboard, token stored
- User logs in → Redirect to dashboard, tasks load
- User logs out → Redirect to login, token cleared
- User closes browser → Reopen, still logged in (persistent session)
- User tries to access dashboard without login → Redirect to login

---

## Environment Variables

```bash
# Backend (.env)
BETTER_AUTH_SECRET="your-256-bit-secret-key-here"  # CRITICAL: Never commit
DATABASE_URL="postgresql://user:pass@host:5432/db"
JWT_ALGORITHM="HS256"
JWT_EXPIRY_DAYS=7

# Frontend (.env.local)
NEXT_PUBLIC_API_URL="http://localhost:8000"        # Development
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"   # Production
```

---

## Better Auth Configuration

### Backend Setup (Python/FastAPI)
```python
# app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Frontend Setup (Next.js)
```typescript
// lib/auth.ts
export async function login(email: string, password: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include' // Include cookies
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  // Store token in localStorage (or use cookie)
  localStorage.setItem('token', data.token);
  return data.user;
}
```

---

## Performance Considerations

- **Token Verification**: Cache decoded tokens in memory (with expiry check)
- **Password Hashing**: Use async bcrypt to avoid blocking event loop
- **Database Queries**: Index on `users.email` for fast lookups
- **Rate Limiting**: Use Redis for distributed rate limiting

---

## Accessibility

- Form labels clearly associated with inputs (htmlFor)
- Error messages announced by screen readers (aria-live="polite")
- Focus management: Focus first error field on validation failure
- Keyboard navigation: Tab through all form fields and buttons
- Visible focus indicators (ring-2 ring-blue-500)

---

## Success Metrics

- User can sign up in < 5 seconds
- User can log in in < 2 seconds
- JWT token verification in < 10ms
- Zero unauthorized access to other users' data (security tests pass)
- 401 errors properly handled (user redirected to login)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
