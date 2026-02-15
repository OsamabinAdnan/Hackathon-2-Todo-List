---
name: stateless-audit
description: Comprehensive stateless architecture audit for chat endpoints and MCP servers, identifying state leaks, memory state issues, database state problems, cache state inconsistencies, and ensuring atomic operation verification. Use when auditing Phase 3 AI Chatbot for statelessness compliance, identifying potential state leaks in chat endpoints, verifying conversation persistence patterns, validating atomic transaction handling, ensuring user isolation in stateless systems, performing compliance checks for multi-user isolation, validating cache invalidation strategies, ensuring request-scoped state management, verifying database transaction boundaries, and confirming no cross-user data leakage in stateless systems.
---

# Stateless Audit Skill

## Overview

This skill provides comprehensive methodologies and tools for auditing stateless architecture implementations, specifically designed for Phase 3 AI Chatbot compliance. The skill enables thorough validation of stateless patterns in chat endpoints and MCP servers, ensuring proper user isolation, conversation persistence, and atomic operation handling while maintaining performance efficiency.

## Core Capabilities

### 1. Memory State Audit
- Identifies in-memory session variables that could persist across requests
- Detects request-scoped state that may leak between users
- Finds global state patterns that compromise user isolation
- Validates proper request-scoped dependency injection

### 2. Database State Verification
- Ensures conversation state is properly persisted to Neon PostgreSQL
- Verifies user isolation through proper foreign key relationships
- Confirms transaction boundaries and atomic operation handling
- Validates conversation persistence patterns

### 3. Cache State Analysis
- Reviews caching mechanisms for cross-user data leakage
- Validates cache key isolation strategies
- Checks cache invalidation respecting user boundaries
- Ensures session data doesn't cross-contaminate

### 4. Atomic Operation Verification
- Confirms each request handles its own transaction lifecycle
- Validates database operation atomicity within requests
- Checks error handling that doesn't leave partial states
- Ensures independent request processing

### 5. Performance Impact Assessment
- Evaluates stateless patterns for efficiency
- Monitors resource utilization across requests
- Validates optimized database query patterns
- Confirms efficient session reconstruction

## Audit Process Workflow

### Phase 1: Memory State Analysis
1. **Scan for Global State Patterns**
   - Identify module-level variables that change during execution
   - Detect singleton patterns that maintain mutable state
   - Check for global configuration objects that get modified
   - Review application-level state that persists across requests

2. **Examine Request-Scoped Dependencies**
   - Verify that request context is properly isolated per request
   - Check that request-scoped dependencies don't leak between requests
   - Confirm middleware doesn't maintain cross-request state
   - Validate that request/response objects are properly scoped

3. **Validate Session Management**
   - Ensure no global variables store user session data
   - Check for class-level attributes that maintain state between calls
   - Look for static/dict objects that maintain state across calls
   - Review FastAPI dependency injection for request-scoped services

### Phase 2: Database State Validation
1. **User Isolation Verification**
   - Verify that conversation IDs are properly user-scoped
   - Check that database queries include user_id filters
   - Confirm foreign key relationships enforce user isolation
   - Validate that conversation history is isolated per user

2. **Transaction Boundary Validation**
   - Ensure each request operates within its own transaction scope
   - Verify that database connections are properly closed
   - Check that transaction rollbacks work correctly
   - Confirm atomic operations don't span multiple requests

3. **Persistence Pattern Review**
   - Validate that conversation state is saved before response
   - Check that database operations complete within request lifecycle
   - Verify that async operations don't create race conditions
   - Confirm data consistency across concurrent requests

### Phase 3: Cache State Analysis
1. **Cross-User Data Leakage Detection**
   - Verify cache keys include user identifiers
   - Check that cached data is properly isolated per user
   - Confirm cache invalidation respects user boundaries
   - Validate that cached sessions don't cross-contaminate

2. **Cache Strategy Validation**
   - Review cache expiration policies for conversation data
   - Check that cache invalidation happens on user logout
   - Verify cache keys follow user-specific naming patterns
   - Confirm cache updates don't affect other users

### Phase 4: Atomic Operation Verification
1. **Request Lifecycle Validation**
   - Ensure each request handles its own transaction lifecycle
   - Verify that database operations are atomic within requests
   - Check that error handling doesn't leave partial states
   - Confirm that each request can be processed independently

2. **Transaction Boundary Confirmation**
   - Validate that database transactions are properly scoped
   - Check that nested transactions are handled correctly
   - Verify that transaction timeouts are appropriately set
   - Confirm that deadlock prevention is implemented

## Validation Checklists

### Memory State Validation Checklist
- [ ] No global variables store user-specific data
- [ ] No class attributes maintain state between requests
- [ ] Request-scoped dependencies are properly isolated
- [ ] Middleware doesn't maintain cross-request state
- [ ] Singleton patterns don't store mutable user data
- [ ] Static variables don't change during execution
- [ ] FastAPI dependencies are request-scoped where appropriate
- [ ] No shared memory objects between user sessions

### Database State Validation Checklist
- [ ] All queries include user_id filtering
- [ ] Foreign key constraints enforce user isolation
- [ ] Conversation data is properly user-scoped
- [ ] Transactions are properly bounded per request
- [ ] Database connections are properly managed
- [ ] Transaction rollbacks work correctly
- [ ] No direct database access without user isolation
- [ ] Conversation persistence follows atomic principles

### Cache State Validation Checklist
- [ ] Cache keys include user identifiers
- [ ] Cached data is properly isolated per user
- [ ] Cache invalidation respects user boundaries
- [ ] Session data doesn't cross-contaminate
- [ ] Cache expiration policies are appropriate
- [ ] Cache updates don't affect other users
- [ ] No global cache without user-specific keys
- [ ] Cache invalidation happens on user logout

### Atomic Operation Validation Checklist
- [ ] Each request handles its own transaction lifecycle
- [ ] Database operations are atomic within requests
- [ ] Error handling doesn't leave partial states
- [ ] Each request can be processed independently
- [ ] Transaction boundaries are properly defined
- [ ] Nested transactions are handled correctly
- [ ] No operations span multiple request boundaries
- [ ] Rollback behavior is properly implemented

## Practical Examples

### Example 1: Memory State Issue Detection
```python
# BAD: Global state that persists across requests
CONVERSATION_CACHE = {}

# GOOD: Request-scoped state management
def get_conversation_service(user_id: str) -> ConversationService:
    return ConversationService(user_id=user_id)
```

### Example 2: Database State Isolation
```python
# BAD: Missing user_id filter
conversation = db.query(Conversation).filter_by(id=conv_id).first()

# GOOD: Proper user isolation
conversation = db.query(Conversation).filter_by(
    id=conv_id,
    user_id=user_id
).first()
```

### Example 3: Cache Key Isolation
```python
# BAD: Non-user-specific cache key
cache_key = f"conversation:{conversation_id}"

# GOOD: User-specific cache key
cache_key = f"conversation:{user_id}:{conversation_id}"
```

### Example 4: Transaction Boundary Validation
```python
# BAD: Transaction spanning multiple requests
class GlobalTransactionManager:
    def __init__(self):
        self.transaction = None

# GOOD: Request-scoped transactions
@router.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest):
    async with db.transaction():
        # All operations within this request
        conversation = await create_conversation(user_id, request)
        message = await save_message(conversation.id, request.message)
        return ChatResponse(message=message)
```

## Automated Testing Templates

### Statelessness Verification Tests
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_user_data_isolation():
    """Test that user A cannot access user B's conversation data"""
    client = TestClient(app)

    # User A creates a conversation
    response_a = client.post("/api/user_a/chat", json={"message": "Hello from A"})
    assert response_a.status_code == 200
    conv_id_a = response_a.json()["conversation_id"]

    # User B creates a conversation
    response_b = client.post("/api/user_b/chat", json={"message": "Hello from B"})
    assert response_b.status_code == 200
    conv_id_b = response_b.json()["conversation_id"]

    # User A should not access User B's conversation
    access_response = client.get(f"/api/user_a/conversations/{conv_id_b}")
    assert access_response.status_code == 404  # Or 403

def test_concurrent_request_isolation():
    """Test that concurrent requests maintain proper isolation"""
    import asyncio
    import threading

    results = []

    def make_request(user_id, message):
        client = TestClient(app)
        response = client.post(f"/api/{user_id}/chat", json={"message": message})
        results.append(response.json())

    # Simulate concurrent requests from different users
    threads = [
        threading.Thread(target=make_request, args=(f"user_{i}", f"message_{i}"))
        for i in range(5)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all requests were processed independently
    assert len(results) == 5
    for result in results:
        assert "conversation_id" in result
```

### Conversation Persistence Tests
```python
def test_conversation_state_persistence():
    """Test that conversation state persists correctly across requests"""
    client = TestClient(app)

    # Start a conversation
    response1 = client.post("/api/test_user/chat", json={"message": "Hello"})
    assert response1.status_code == 200
    conv_id = response1.json()["conversation_id"]

    # Add to the conversation
    response2 = client.post(f"/api/test_user/chat/{conv_id}", json={"message": "How are you?"})
    assert response2.status_code == 200

    # Retrieve conversation history
    history_response = client.get(f"/api/test_user/conversations/{conv_id}/history")
    assert history_response.status_code == 200
    history = history_response.json()

    # Verify both messages are present
    assert len(history) == 2
    assert any(msg["content"] == "Hello" for msg in history)
    assert any(msg["content"] == "How are you?" for msg in history)

def test_transaction_rollback_on_error():
    """Test that database operations are properly rolled back on error"""
    client = TestClient(app)

    # Create a conversation with invalid data that should trigger rollback
    response = client.post("/api/test_user/chat", json={
        "message": "This should fail",
        "invalid_field": "invalid_value"  # This should cause an error
    })

    # Verify error response
    assert response.status_code == 422

    # Verify no partial data was saved
    history_response = client.get("/api/test_user/conversations")
    assert history_response.status_code == 200
    history = history_response.json()
    # Should not contain the failed conversation
    assert not any("This should fail" in str(conv) for conv in history)
```

## Compliance Requirements

### Phase 3 Stateless Architecture Requirements
- [ ] Chat endpoints must be stateless across requests
- [ ] User data must be isolated between concurrent users
- [ ] Conversation state must persist correctly in database
- [ ] No in-memory state should persist between requests
- [ ] Cache mechanisms must respect user boundaries
- [ ] Each request must handle its own transaction lifecycle
- [ ] Database operations must be atomic and isolated
- [ ] Performance impact of stateless patterns is acceptable
- [ ] Automated tests verify statelessness properties
- [ ] Multi-user isolation is maintained at all levels

## Risk Mitigation Strategies

### Memory State Risks
- **Risk**: Global variables storing user data
- **Mitigation**: Use dependency injection with request-scoped services
- **Validation**: Regular code reviews for global state usage

### Database State Risks
- **Risk**: Missing user_id filters in queries
- **Mitigation**: Always include user_id in WHERE clauses for user data
- **Validation**: Automated query analysis tools

### Cache State Risks
- **Risk**: Cross-user data leakage through cache
- **Mitigation**: Include user_id in all cache keys for user data
- **Validation**: Cache access pattern monitoring

### Transaction Risks
- **Risk**: Partial state updates on failure
- **Mitigation**: Use database transactions for related operations
- **Validation**: Transaction boundary testing

## Resources

This skill provides comprehensive resources for stateless architecture validation:

### scripts/
Contains executable scripts for automated stateless architecture validation:
- `memory_state_audit.py` - Automated detection of global state patterns
- `database_isolation_checker.py` - Verification of user data isolation
- `cache_key_validator.py` - Validation of cache key isolation patterns
- `transaction_boundary_tester.py` - Testing of atomic operation boundaries

### references/
Includes detailed documentation and reference materials:
- `stateless_patterns.md` - Comprehensive patterns for stateless architecture
- `database_schema_validation.md` - Guidelines for user-isolated database design
- `cache_strategy_guidelines.md` - Best practices for cache isolation
- `performance_impact_analysis.md` - Assessment methodologies for stateless patterns

### assets/
Provides templates and boilerplate for testing:
- `test_templates/` - Automated test templates for stateless validation
- `validation_scripts/` - Pre-built validation scripts for common scenarios
