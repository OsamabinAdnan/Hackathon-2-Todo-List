# Cache Strategy Guidelines for Stateless Systems

This document provides comprehensive guidelines for implementing cache strategies that maintain statelessness while improving performance in the Phase 3 AI Chatbot system.

## Core Cache Principles

### 1. User Isolation in Cache
- All user-specific cache keys must include user identifier
- Cache operations must respect user boundaries
- No cross-user data leakage through cache mechanisms
- Proper cache invalidation per user session

### 2. Cache Key Design
- Use consistent naming patterns that include user_id
- Separate user-specific and shared cache keys
- Include versioning information where appropriate
- Use descriptive but concise key names

### 3. Cache Expiration Strategy
- Set appropriate TTL for different types of data
- Implement sliding expiration for active sessions
- Use cache-aside pattern for database-backed data
- Consider cache-invalidation patterns for consistency

## Cache Key Naming Conventions

### User-Specific Cache Keys
```python
# Pattern: namespace:user_id:resource:identifier
conversation_cache_key = f"conversation:{user_id}:{conversation_id}"
user_profile_cache_key = f"profile:{user_id}:basic_info"
user_settings_cache_key = f"settings:{user_id}:preferences"
```

### Shared/Global Cache Keys
```python
# Pattern: namespace:resource:identifier (no user_id)
global_config_cache_key = f"config:app:version"
shared_lookup_cache_key = f"lookup:countries:list"
```

### Parameterized Cache Keys
```python
# Include all parameters that affect the result
filtered_search_key = f"search:{user_id}:{query_hash}:{filters_hash}"
paginated_results_key = f"results:{user_id}:{query_id}:{page_num}:{page_size}"
```

## Cache Implementation Patterns

### Pattern 1: User-Specific Conversation Cache
```python
# GOOD: User-specific cache key
class ConversationCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_conversation_history(self, user_id: str, conversation_id: str):
        cache_key = f"conversation:{user_id}:{conversation_id}:history"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # Load from database
        history = self.load_from_db(user_id, conversation_id)

        # Cache for 1 hour
        self.redis.setex(cache_key, 3600, json.dumps(history))
        return history

    def invalidate_user_conversations(self, user_id: str):
        # Invalidate all conversation caches for this user
        pattern = f"conversation:{user_id}:*"
        # Redis SCAN and DELETE implementation needed
```

### Pattern 2: Request-Scoped Cache Helper
```python
# GOOD: Helper that ensures user isolation
class CacheHelper:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_user_cache(self, user_id: str, cache_type: str, identifier: str):
        cache_key = f"{cache_type}:{user_id}:{identifier}"
        return self.redis.get(cache_key)

    def set_user_cache(self, user_id: str, cache_type: str, identifier: str, data, ttl: int = 3600):
        cache_key = f"{cache_type}:{user_id}:{identifier}"
        self.redis.setex(cache_key, ttl, json.dumps(data))

    def invalidate_user_cache(self, user_id: str, cache_type: str, identifier: str = None):
        if identifier:
            cache_key = f"{cache_type}:{user_id}:{identifier}"
            self.redis.delete(cache_key)
        else:
            # Invalidate all caches of this type for user
            pattern = f"{cache_type}:{user_id}:*"
            # Implementation for deleting multiple keys
```

## Cache Strategies

### 1. Cache-Aside Pattern (Recommended)
```python
# GOOD: Cache-aside pattern with user isolation
async def get_conversation_with_cache(user_id: str, conversation_id: str, db: Session):
    cache_key = f"conversation:{user_id}:{conversation_id}"

    # Try cache first
    cached_result = await cache.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    # Load from database
    conversation = db.query(Conversation).filter_by(
        id=conversation_id,
        user_id=user_id  # Ensure user isolation
    ).first()

    if conversation:
        # Cache the result
        await cache.setex(cache_key, 3600, json.dumps(conversation.to_dict()))

    return conversation
```

### 2. Write-Through Pattern
```python
# GOOD: Write-through with cache update
async def update_conversation_cache(user_id: str, conversation_id: str, data: dict):
    cache_key = f"conversation:{user_id}:{conversation_id}"

    # Update database
    await update_database(user_id, conversation_id, data)

    # Update cache synchronously
    await cache.setex(cache_key, 3600, json.dumps(data))
```

### 3. Cache-Invalidation Pattern
```python
# GOOD: Proper cache invalidation
async def delete_conversation_and_invalidate(user_id: str, conversation_id: str):
    # Delete from database
    await delete_from_database(user_id, conversation_id)

    # Invalidate cache
    cache_key = f"conversation:{user_id}:{conversation_id}"
    await cache.delete(cache_key)

    # Also invalidate related caches
    user_conv_list_key = f"conversations:{user_id}:list"
    await cache.delete(user_conv_list_key)
```

## Common Cache Anti-Patterns

### Anti-Pattern 1: Global Cache Without User Isolation
```python
# BAD: Global cache key that ignores user
GLOBAL_CACHE = {}

def get_conversation(conversation_id: str):
    # This allows any user to access any conversation through cache!
    cache_key = f"conversation:{conversation_id}"  # Missing user_id!
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
    # ...
```

### Anti-Pattern 2: Shared Cache for User Data
```python
# BAD: Using shared cache for user-specific data
def get_user_profile(user_id: str):
    # This allows user A to potentially get user B's profile if keys collide
    cache_key = f"profile:{user_id}"  # If user_id isn't properly isolated
    return cache.get(cache_key)
```

### Anti-Pattern 3: Inadequate Cache Invalidation
```python
# BAD: Not invalidating cache after update
async def update_conversation(user_id: str, conversation_id: str, data: dict):
    # Update database
    await update_database(user_id, conversation_id, data)
    # FORGOTTEN: Not invalidating cache - stale data will be served!
```

## Cache Performance Considerations

### 1. TTL Strategy
- Short TTL for frequently changing data (5-15 minutes)
- Medium TTL for semi-static data (1-4 hours)
- Long TTL for rarely changing data (24+ hours)
- No TTL for session-specific temporary data

### 2. Cache Size Management
- Monitor cache hit/miss ratios
- Implement LRU eviction policies
- Set maximum cache sizes to prevent memory issues
- Use cache warming for critical data

### 3. Cache Tiering
- L1: In-memory cache for fastest access (small, frequently accessed data)
- L2: Redis/Memcached for larger datasets
- L3: Database for permanent storage and cache misses

## Cache Security Considerations

### 1. Data Isolation
- Validate user_id in cache keys to prevent injection
- Use proper escaping for dynamic key components
- Implement access controls at the cache layer

### 2. Sensitive Data
- Don't cache sensitive data unless encrypted
- Implement proper encryption for cached PII
- Regular cache purging for sensitive information

### 3. Cache Poisoning Prevention
- Validate data before caching
- Implement cache key validation
- Monitor for unusual access patterns

## Cache Monitoring and Validation

### Key Metrics to Monitor
- Cache hit ratio
- Average response time with/without cache
- Memory usage
- Number of cache keys per user
- Cache invalidation frequency

### Validation Techniques
- Regular cache key audits
- User isolation testing
- Performance benchmarking
- Memory leak detection

## Cache Testing Strategies

### 1. Isolation Testing
```python
# Test that users can't access each other's cached data
def test_cache_isolation():
    # User A caches data
    result_a = get_conversation_with_cache("user_a", "conv_123", db)

    # User B should not get User A's cached data
    result_b = get_conversation_with_cache("user_b", "conv_123", db)
    assert result_b is None  # Should query DB and find nothing
```

### 2. Cache Behavior Testing
```python
# Test cache get/set/invalidate behavior
def test_cache_lifecycle():
    user_id = "test_user"
    conv_id = "test_conv"

    # Initially not in cache
    result = get_conversation_with_cache(user_id, conv_id, db)
    # Should query DB

    # Second call should hit cache
    result2 = get_conversation_with_cache(user_id, conv_id, db)
    # Should return cached result

    # Update and invalidate
    update_conversation_and_invalidate(user_id, conv_id, new_data)

    # Third call should miss cache and query DB again
    result3 = get_conversation_with_cache(user_id, conv_id, db)
```