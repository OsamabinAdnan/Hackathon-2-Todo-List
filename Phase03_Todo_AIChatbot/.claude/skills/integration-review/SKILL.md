---
name: integration-review
description: Comprehensive integration review for Phase 3 Compliance Reviewer to verify Phase 2-3 seamlessness. Performs API Contract Verification (JWT validation consistency, error responses, data models), Data Consistency Validation (task/user tables), Security Boundary Validation, Model Consistency Check, Regression Testing, and Endpoint Mapping Verification. Use when validating that Phase 3 chatbot integrates seamlessly with Phase 2 backend systems, ensuring no breaking changes to existing functionality and consistent security measures across both phases.
---

# Integration Review Skill for Phase 3 Compliance Reviewer

## Overview

This skill provides comprehensive validation procedures to ensure seamless integration between Phase 2 (Full-Stack Web Application) and Phase 3 (AI Chatbot) of the Todo application. The skill enables the Phase 3 Compliance Reviewer agent to systematically verify that all components work harmoniously while maintaining the integrity of existing Phase 2 functionality.

## Core Validation Capabilities

### 1. API Contract Verification
Validates that Phase 3 chat endpoints use the same JWT validation as Phase 2, maintain consistent error responses, and use matching data models.

**Validation Steps:**
- Compare JWT token validation middleware between Phase 2 and Phase 3 endpoints
- Verify consistent HTTP status codes (401, 403, 404, 500, etc.) across both phases
- Validate that request/response schemas match between Phase 2 REST endpoints and Phase 3 chat endpoints
- Confirm that authentication headers and token formats are identical

**Checklist:**
- [ ] JWT validation middleware uses same algorithm (HS256) and secret management
- [ ] User ID extraction from tokens follows identical pattern in both phases
- [ ] Error response format is consistent (e.g., `{"error": "message", "code": "ERROR_CODE"}`)
- [ ] Data serialization/deserialization follows same patterns
- [ ] API versioning strategy is consistent across both phases

### 2. Data Consistency Validation
Ensures that the chatbot operates on the same Task/User database tables as Phase 2, maintaining data integrity and consistency.

**Validation Steps:**
- Verify that both phases connect to the same PostgreSQL database instance
- Confirm that SQLModel models are identical or compatible between phases
- Validate that database connection strings and configurations match
- Test that data created in Phase 2 is accessible in Phase 3 and vice versa

**Checklist:**
- [ ] Both phases use same database connection parameters
- [ ] SQLModel Task and User models are identical or properly migrated
- [ ] Database indexes and constraints are consistent
- [ ] Foreign key relationships are maintained across both phases
- [ ] Data validation rules are applied consistently

### 3. Security Boundary Validation
Confirms that all security measures work identically in both phases, ensuring no security gaps are introduced.

**Validation Steps:**
- Verify that user isolation is maintained (user A cannot access user B's data)
- Confirm that authentication and authorization checks are applied consistently
- Validate that input sanitization and validation are identical
- Test that rate limiting and other security controls are properly implemented

**Checklist:**
- [ ] User ID validation prevents cross-user data access
- [ ] JWT token expiration is handled identically in both phases
- [ ] Input validation and sanitization are consistent
- [ ] Rate limiting applies to both Phase 2 and Phase 3 endpoints
- [ ] SQL injection prevention is implemented identically

### 4. Model Consistency Check
Validates that data models (Task, User, etc.) are consistent across both phases.

**Validation Steps:**
- Compare SQLModel definitions in both phases
- Verify that database schema matches model definitions
- Confirm that serialization/deserialization patterns are identical
- Test that field types, constraints, and validations match

**Checklist:**
- [ ] Task model fields are identical in both phases
- [ ] User model fields and relationships are consistent
- [ ] Enum types and validation constraints match
- [ ] Default values and nullable fields are consistent
- [ ] Database migration scripts are applied to both phases

### 5. Regression Testing
Provides test scenarios to ensure Phase 2 functionality isn't broken by Phase 3 integration.

**Validation Steps:**
- Execute Phase 2 critical user flows with Phase 3 components active
- Verify that existing API endpoints continue to function
- Test that database operations from Phase 2 still work correctly
- Confirm that frontend functionality remains intact

**Test Scenarios:**
- [ ] User login/logout functionality works as expected
- [ ] Task CRUD operations function correctly
- [ ] User data isolation is maintained
- [ ] Existing API endpoints return expected responses
- [ ] Database transactions complete successfully
- [ ] Authentication flows work without interruption

### 6. Endpoint Mapping Verification
Confirms that MCP tools map correctly to Phase 2 database operations.

**Validation Steps:**
- Verify that MCP tool endpoints correspond to appropriate Phase 2 database operations
- Test that tool parameters map to correct database fields
- Confirm that error handling is consistent between tools and direct database access
- Validate that transaction management is properly handled

**Checklist:**
- [ ] MCP tool endpoints access same database tables as Phase 2
- [ ] Tool parameters map correctly to model fields
- [ ] Error responses from tools match Phase 2 patterns
- [ ] Transaction boundaries are properly defined
- [ ] Concurrency controls work identically

## Validation Procedures

### Pre-Integration Checklist
Before validating Phase 2-3 integration:

1. **Environment Setup**
   - Ensure both Phase 2 and Phase 3 services are running
   - Verify database connectivity for both phases
   - Confirm that configuration files match between phases

2. **Baseline Testing**
   - Execute Phase 2 functionality independently to establish baseline
   - Document expected responses and behaviors
   - Run existing test suites to confirm Phase 2 stability

3. **Documentation Review**
   - Review Phase 2 API documentation
   - Examine database schema documentation
   - Verify security requirements and constraints

### Integration Validation Workflow

1. **API Contract Verification**
   ```
   # Compare JWT validation
   - Extract JWT middleware from Phase 2 backend/app/middleware/auth.py
   - Compare with Phase 3 JWT implementation
   - Validate token format and validation logic
   ```

2. **Data Consistency Testing**
   ```
   # Test data access consistency
   - Create task via Phase 2 API
   - Access same task via Phase 3
   - Verify data integrity and consistency
   ```

3. **Security Boundary Testing**
   ```
   # Test user isolation
   - Authenticate as User A
   - Attempt to access User B's data through Phase 3
   - Verify access is properly denied
   ```

4. **Model Consistency Verification**
   ```
   # Compare model definitions
   - Extract SQLModel definitions from Phase 2
   - Compare with Phase 3 model definitions
   - Validate field types, constraints, and relationships
   ```

5. **Regression Testing**
   ```
   # Execute critical user flows
   - Test Phase 2 functionality with Phase 3 active
   - Verify no performance degradation
   - Confirm all existing features still work
   ```

## Practical Examples

### Example 1: API Contract Verification
```python
# Phase 2 JWT Validation (backend/app/middleware/auth.py)
def validate_token(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Phase 3 must use identical validation logic
# Verify both return same error formats and status codes
```

### Example 2: Data Consistency Validation
```python
# Phase 2 Task Creation
POST /api/{user_id}/tasks
Request: {"title": "Test task", "description": "Test description", "priority": "medium"}
Response: {"id": 1, "title": "Test task", "user_id": 123, ...}

# Phase 3 MCP Tool should access same database record
# Verify that the same task record is accessible through both interfaces
```

### Example 3: Security Boundary Validation
```python
# Test user isolation
# User A creates task with user_id=1
# User B should not be able to access task with user_id=1 through Phase 3
# Both phases should enforce identical user_id filtering
```

## Testing Scenarios

### Scenario 1: User Authentication Consistency
- Authenticate user in Phase 2
- Access Phase 3 with same token
- Verify identical user context and permissions

### Scenario 2: Task Data Synchronization
- Create task via Phase 2 UI
- Query task via Phase 3 chatbot
- Verify data consistency and accessibility

### Scenario 3: Error Handling Consistency
- Trigger authentication error in Phase 2
- Trigger same error in Phase 3
- Verify identical error response format and codes
