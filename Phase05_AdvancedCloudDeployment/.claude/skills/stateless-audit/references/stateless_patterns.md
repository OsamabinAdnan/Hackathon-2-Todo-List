# Stateless Architecture Patterns

This document outlines the key patterns and anti-patterns for implementing stateless systems, particularly for chat endpoints and MCP servers in the Phase 3 AI Chatbot.

## Core Stateless Principles

### 1. Request Independence
- Each request must contain all necessary information to be processed
- No reliance on server-side session state between requests
- Client provides authentication tokens with each request
- All context required for processing is passed in the request

### 2. State Storage Patterns
- **Database Storage**: Store conversation state in persistent database
- **Token-Based Context**: Encode minimal session state in JWT tokens
- **Client-Side Storage**: Allow clients to maintain their own state where appropriate
- **External Services**: Use dedicated services for state management (Redis, etc.)

### 3. Atomic Operations
- Each request performs a complete, atomic operation
- Database transactions are contained within single requests
- No long-running operations that span multiple requests
- Proper error handling with complete rollback on failure

## Common Stateless Patterns

### Pattern 1: Request-Scoped Service Dependencies
```python
# GOOD: Service created per request with user context
@router.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    # Service is created with user context for this request only
    conversation_service = ConversationService(db, user_id)
    result = await conversation_service.process(request)
    return result
```

### Pattern 2: Database-First Conversation Storage
```python
# GOOD: Conversation state stored in database, retrieved per request
async def get_conversation_history(user_id: str, conversation_id: str, db: Session):
    # Always query with user_id to ensure isolation
    conversation = db.query(Conversation).filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation.messages
```

### Pattern 3: Token-Based Authentication
```python
# GOOD: Authentication verified per request from token
def verify_user_from_token(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "")
    payload = decode_jwt(token)
    return payload["user_id"]  # Extract user_id from token
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Global State Storage
```python
# BAD: Global variable storing user conversations
USER_CONVERSATIONS = {}

@router.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest):
    # This stores data globally - violates statelessness!
    if user_id not in USER_CONVERSATIONS:
        USER_CONVERSATIONS[user_id] = []
    USER_CONVERSATIONS[user_id].append(request.message)
    return {"response": "processed"}
```

### Anti-Pattern 2: Cross-Request Session Objects
```python
# BAD: Persistent session object between requests
class GlobalSessionManager:
    def __init__(self):
        self.sessions = {}

    def get_session(self, user_id: str):
        # This creates persistent state across requests!
        if user_id not in self.sessions:
            self.sessions[user_id] = {"conversation": []}
        return self.sessions[user_id]

SESSION_MANAGER = GlobalSessionManager()
```

### Anti-Pattern 3: Missing User Isolation
```python
# BAD: Query without user_id filter
async def get_conversation(conversation_id: str, db: Session):
    # Missing user_id filter - any user can access any conversation!
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    return conversation
```

## State Management Strategies

### 1. Conversation State Management
- Store conversation context in database with user_id foreign key
- Load conversation state at beginning of each request
- Save updated state before returning response
- Use database transactions to ensure atomic updates

### 2. Authentication State Management
- Store authentication in JWT tokens passed with each request
- Validate token and extract user_id on each request
- Never store authentication state on server between requests
- Implement proper token refresh mechanisms

### 3. Caching Strategies
- Use cache keys that include user_id for user-specific data
- Implement proper cache invalidation on user logout
- Cache non-user-specific data separately
- Use time-based expiration to prevent stale data

## Performance Considerations

### Efficient Database Queries
- Use indexed fields for user_id in all queries
- Implement proper pagination for large conversation histories
- Use connection pooling for database operations
- Consider read replicas for high-read scenarios

### Caching Effectiveness
- Cache expensive operations that don't vary by user
- Use user-specific cache keys for personalized data
- Implement cache warming strategies for common requests
- Monitor cache hit rates and adjust TTL accordingly

## Error Handling in Stateless Systems

### Consistent Error Responses
- Always return consistent error formats
- Include appropriate HTTP status codes
- Don't expose internal state in error messages
- Log errors with sufficient context for debugging

### Recovery from Failures
- Design operations to be idempotent where possible
- Implement proper retry mechanisms
- Use circuit breakers for external dependencies
- Maintain data consistency during partial failures

## Testing Stateless Systems

### Isolation Testing
- Verify that users cannot access other users' data
- Test concurrent requests from different users
- Validate that state changes don't affect other users
- Test error conditions and rollback behavior

### Load Testing
- Verify performance under concurrent load
- Test database connection limits
- Validate cache effectiveness under load
- Monitor resource usage patterns