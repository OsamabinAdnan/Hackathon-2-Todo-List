---
name: security-audit
description: Scan generated authentication code for vulnerabilities and suggest improvements like rate limiting, HTTPS enforcement, and stateless auth validation. Use when (1) Reviewing authentication/authorization code for security flaws, (2) Auditing JWT token implementation for proper validation and secret management, (3) Checking for common vulnerabilities (SQL injection, XSS, CSRF, session fixation), (4) Validating user isolation in database queries, (5) Ensuring HTTPS enforcement and secure cookie settings in production, (6) Iteratively refining security implementations based on audit findings.
---

# Security Audit Skill

Comprehensively scan and audit authentication, authorization, and data access code for security vulnerabilities with actionable remediation recommendations.

## Audit Categories

### 1. Authentication Security

#### JWT Token Implementation
**Check for:**
- [ ] **Secret Key Strength**: JWT_SECRET_KEY is at least 32 characters (256 bits)
- [ ] **Secret Storage**: Secrets stored in environment variables, NOT hardcoded
- [ ] **Algorithm Security**: Using HS256 or RS256 (avoid HS512 or "none")
- [ ] **Token Expiry**: Access tokens have reasonable expiration (7-30 days max)
- [ ] **Claims Validation**: Token validation checks `exp`, `iat`, `user_id`, and `type` claims
- [ ] **Token Type Distinction**: Separate access and refresh token types with validation

**Vulnerable Code Example:**
```python
# ❌ INSECURE: Hardcoded secret, weak algorithm
SECRET_KEY = "my-secret"  # Too short!
jwt.encode(payload, SECRET_KEY, algorithm="HS512")  # Weak algorithm
```

**Secure Code Example:**
```python
# ✅ SECURE: Environment variable, strong algorithm
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters")

jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Audit Script:**
```python
# scripts/audit_jwt_security.py
import re
import os

def audit_jwt_implementation(file_path):
    """Audit JWT token implementation for security issues."""
    with open(file_path, 'r') as f:
        content = f.read()

    issues = []

    # Check for hardcoded secrets
    if re.search(r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', content):
        issues.append("CRITICAL: Hardcoded SECRET_KEY found. Use environment variables.")

    # Check for weak algorithms
    if 'algorithm="none"' in content or 'algorithm="HS512"' in content:
        issues.append("HIGH: Weak JWT algorithm detected. Use HS256 or RS256.")

    # Check for missing token expiry
    if 'jwt.encode' in content and 'exp' not in content:
        issues.append("MEDIUM: Token expiry ('exp' claim) not set.")

    # Check for environment variable loading
    if 'JWT_SECRET_KEY' in content and 'os.getenv' not in content:
        issues.append("HIGH: JWT_SECRET_KEY not loaded from environment.")

    return issues
```

#### Password Security
**Check for:**
- [ ] **Hashing Algorithm**: Using bcrypt, argon2, or scrypt (NOT MD5/SHA1)
- [ ] **Salt Generation**: Salts generated per-password (automatic with bcrypt)
- [ ] **Password Complexity**: Minimum 8 characters enforced
- [ ] **Timing Attack Prevention**: Constant-time password comparison
- [ ] **Password Reset**: Secure token generation for password resets

**Vulnerable Code Example:**
```python
# ❌ INSECURE: Plain text password storage
user.password = request_data.password  # NO!

# ❌ INSECURE: Weak hashing
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()  # Broken!
```

**Secure Code Example:**
```python
# ✅ SECURE: bcrypt with automatic salting
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. Authorization and Access Control

#### User Isolation
**Check for:**
- [ ] **Path Parameter Validation**: user_id from URL matches authenticated user
- [ ] **Query Filtering**: All queries filter by `current_user.id`
- [ ] **Ownership Verification**: Resource ownership checked before access
- [ ] **Forbidden vs Not Found**: Return 403 for unauthorized access, 404 for missing resources
- [ ] **No Shared Database Sessions**: Each user query scoped to their data

**Vulnerable Code Example:**
```python
# ❌ INSECURE: No user isolation check
@router.get("/api/{user_id}/tasks")
async def list_tasks(user_id: str, session: Session = Depends(get_session)):
    # Missing: current_user verification!
    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks  # Any user can access any user_id!
```

**Secure Code Example:**
```python
# ✅ SECURE: User isolation enforced
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Query scoped to current user
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id)
    ).all()
    return tasks
```

**Audit Script:**
```python
# scripts/audit_user_isolation.py
import ast

def audit_user_isolation(file_path):
    """Audit endpoints for proper user isolation."""
    with open(file_path, 'r') as f:
        content = f.read()

    issues = []

    # Check if endpoints have get_current_user dependency
    if '@router.' in content and 'Depends(get_current_user)' not in content:
        issues.append("HIGH: Protected endpoint missing authentication dependency.")

    # Check for user_id validation
    if 'user_id' in content and 'current_user.id != user_id' not in content:
        issues.append("CRITICAL: Missing user_id validation against authenticated user.")

    # Check for proper query filtering
    if 'select(Task)' in content and 'Task.user_id == current_user.id' not in content:
        issues.append("CRITICAL: Query not filtered by current user.")

    return issues
```

### 3. Injection Prevention

#### SQL Injection
**Check for:**
- [ ] **Parameterized Queries**: Using SQLModel/SQLAlchemy ORM (NOT string concatenation)
- [ ] **Input Validation**: Pydantic models validate all inputs
- [ ] **No Raw SQL**: Avoid `session.execute(text(query))` with user input
- [ ] **Whitelist Filtering**: Sort/filter parameters use whitelisted values

**Vulnerable Code Example:**
```python
# ❌ INSECURE: SQL injection vulnerability
@router.get("/api/tasks")
async def search_tasks(query: str, session: Session):
    # String concatenation with user input!
    sql = f"SELECT * FROM tasks WHERE title LIKE '%{query}%'"
    results = session.execute(text(sql)).all()  # VULNERABLE!
    return results
```

**Secure Code Example:**
```python
# ✅ SECURE: Parameterized query with ORM
@router.get("/api/tasks")
async def search_tasks(
    query: str = Query(..., max_length=200),  # Length validation
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # ORM handles parameterization automatically
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .where(Task.title.contains(query))  # Safe parameterization
    ).all()
    return tasks
```

#### Cross-Site Scripting (XSS)
**Check for:**
- [ ] **Response Serialization**: Using Pydantic response models (auto-escapes)
- [ ] **Content-Type Headers**: Proper `application/json` content type
- [ ] **No Direct HTML**: Never returning raw HTML from API
- [ ] **Frontend Sanitization**: React/Vue auto-escapes by default

**Secure Practice:**
```python
# ✅ SECURE: Pydantic response model automatically serializes
@router.get("/api/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(...):
    tasks = session.exec(query).all()
    return tasks  # Pydantic serializes safely
```

### 4. Session and Token Security

#### Token Storage and Transmission
**Check for:**
- [ ] **HTTPS Only**: Production enforces HTTPS for token transmission
- [ ] **httpOnly Cookies**: Cookies not accessible via JavaScript (prevents XSS theft)
- [ ] **Secure Flag**: Cookies marked `secure=True` (HTTPS only)
- [ ] **SameSite Attribute**: Set to `lax` or `strict` (CSRF protection)
- [ ] **Token Blacklisting**: Logout invalidates tokens (Redis or database)

**Vulnerable Code Example:**
```python
# ❌ INSECURE: Token in localStorage (vulnerable to XSS)
# Frontend code
localStorage.setItem('access_token', token)  # NO!
```

**Secure Code Example:**
```python
# ✅ SECURE: httpOnly cookie
from fastapi.responses import Response

@router.post("/api/auth/login")
async def login(response: Response, ...):
    access_token = create_access_token(user_id=user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # HTTPS only
        samesite="lax", # CSRF protection
        max_age=7 * 24 * 60 * 60
    )

    return {"message": "Login successful"}
```

#### Token Blacklisting
**Check for:**
- [ ] **Logout Implementation**: Tokens blacklisted on logout
- [ ] **TTL Matching**: Blacklist expiry matches token expiry
- [ ] **Blacklist Check**: Middleware checks blacklist before accepting tokens
- [ ] **Redis or Database**: Blacklist stored in fast datastore

**Secure Implementation:**
```python
# ✅ SECURE: Token blacklist with Redis
from redis import Redis

redis_client = Redis(host="localhost", port=6379)

def blacklist_token(token: str, ttl_seconds: int):
    redis_client.setex(f"blacklist:{token}", ttl_seconds, "1")

def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}") == 1

# In get_current_user dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    # Check blacklist before accepting token
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    payload = decode_access_token(token)
    # ... rest of authentication
```

### 5. Rate Limiting and DoS Prevention

**Check for:**
- [ ] **Login Rate Limiting**: Max 5 attempts per minute per IP
- [ ] **Signup Rate Limiting**: Prevent automated account creation
- [ ] **Refresh Token Rate Limiting**: Prevent token refresh abuse
- [ ] **Global Rate Limiting**: API-wide limits (e.g., 100 req/min)
- [ ] **Per-User Limits**: Authenticated user rate limits

**Implementation:**
```python
# ✅ SECURE: Rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(...):
    ...

@router.post("/api/auth/signup")
@limiter.limit("3/hour")  # Max 3 signups per hour
async def signup(...):
    ...

@router.get("/api/{user_id}/tasks")
@limiter.limit("100/minute")  # Per-user endpoint limit
async def list_tasks(...):
    ...
```

### 6. HTTPS and Transport Security

**Check for:**
- [ ] **HTTPS Redirect Middleware**: HTTP requests redirected to HTTPS
- [ ] **HSTS Header**: Strict-Transport-Security header set
- [ ] **Secure Headers**: X-Content-Type-Options, X-Frame-Options, CSP
- [ ] **Certificate Validation**: Valid SSL/TLS certificates in production
- [ ] **TLS Version**: Minimum TLS 1.2 or higher

**Implementation:**
```python
# ✅ SECURE: HTTPS enforcement and security headers
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response
```

### 7. CORS Configuration

**Check for:**
- [ ] **Allowed Origins**: Specific domains, NOT wildcard `*`
- [ ] **Credentials Support**: `allow_credentials=True` only with specific origins
- [ ] **Allowed Methods**: Only necessary HTTP methods
- [ ] **Exposed Headers**: Minimal header exposure

**Vulnerable Code Example:**
```python
# ❌ INSECURE: Wildcard CORS with credentials
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any domain!
    allow_credentials=True,  # DANGEROUS with wildcard
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Secure Code Example:**
```python
# ✅ SECURE: Specific origins, controlled methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Only needed methods
    allow_headers=["Content-Type", "Authorization"],  # Only needed headers
    max_age=3600  # Cache preflight for 1 hour
)
```

## Security Audit Checklist

### Authentication & Authorization
- [ ] JWT secrets are 32+ characters and stored in environment variables
- [ ] Passwords hashed with bcrypt/argon2 (NOT MD5/SHA1)
- [ ] Token expiry configured (access: 7 days, refresh: 30 days)
- [ ] User isolation enforced: `current_user.id == user_id`
- [ ] All queries filter by authenticated user
- [ ] Token blacklisting implemented for logout
- [ ] Rate limiting applied to login/signup endpoints (5/min, 3/hour)

### Injection Prevention
- [ ] Using SQLModel ORM (NO raw SQL with user input)
- [ ] Pydantic models validate all request inputs
- [ ] Response models serialize outputs (XSS prevention)
- [ ] Sort/filter parameters use whitelisted values

### Transport Security
- [ ] HTTPS enforced in production (HTTPSRedirectMiddleware)
- [ ] Security headers set (HSTS, X-Content-Type-Options, X-Frame-Options, CSP)
- [ ] Cookies use `httponly=True`, `secure=True`, `samesite="lax"`
- [ ] CORS configured with specific origins (NO wildcard `*`)

### Session Management
- [ ] Tokens invalidated on logout (blacklist or database)
- [ ] "Logout all devices" functionality implemented
- [ ] Concurrent session tracking (optional)
- [ ] Session fixation prevented (new tokens on password change)

### Error Handling
- [ ] Generic error messages (don't leak implementation details)
- [ ] 401 for authentication failures, 403 for authorization failures
- [ ] Sensitive data NOT logged (passwords, tokens, secrets)
- [ ] Stack traces hidden in production

### Dependencies & Updates
- [ ] Dependencies scanned for vulnerabilities (`pip-audit`, `safety`)
- [ ] Regular updates applied to FastAPI, SQLModel, PyJWT
- [ ] `.env` file NOT committed to version control
- [ ] Secrets rotation plan documented

## Automated Audit Tools

### 1. Bandit (Python Security Linter)
```bash
# Install
pip install bandit

# Run security scan
bandit -r backend/ -f json -o security-report.json

# Common issues detected:
# - Hardcoded secrets
# - Weak cryptography
# - SQL injection risks
```

### 2. Safety (Dependency Vulnerability Scanner)
```bash
# Install
pip install safety

# Check dependencies
safety check --json

# Outputs known vulnerabilities in dependencies
```

### 3. pip-audit (Official Python Auditing Tool)
```bash
# Install
pip install pip-audit

# Audit installed packages
pip-audit --format json
```

## Remediation Priority Levels

### CRITICAL (Fix Immediately)
- Hardcoded secrets
- Missing user isolation checks
- SQL injection vulnerabilities
- No HTTPS enforcement in production

### HIGH (Fix Within 24 Hours)
- Weak password hashing (MD5/SHA1)
- Missing rate limiting on auth endpoints
- Wildcard CORS with credentials
- No token blacklisting on logout

### MEDIUM (Fix Within 1 Week)
- Missing security headers (HSTS, CSP)
- Insufficient token expiry (> 30 days)
- Missing input validation
- Generic error responses leaking info

### LOW (Fix When Possible)
- Outdated dependencies (no known CVEs)
- Missing audit logging
- Incomplete session tracking

## Quality Checklist

- [ ] All CRITICAL and HIGH issues resolved
- [ ] Automated security scans integrated into CI/CD
- [ ] Security headers configured and tested
- [ ] HTTPS enforced in production environment
- [ ] Rate limiting applied to sensitive endpoints
- [ ] User isolation verified in all protected routes
- [ ] Token management follows best practices
- [ ] Dependencies up-to-date with no known vulnerabilities

## References

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **FastAPI Security**: https://fastapi.tiangolo.com/advanced/security/
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8725
- **Auth Spec**: `@specs/features/authentication.md` for project requirements
