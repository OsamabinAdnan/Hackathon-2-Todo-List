# ADR-003: Conversation Persistence Model

## Status
Proposed

## Date
2026-01-13

## Context
The AI chatbot needs to maintain conversation history across sessions for context and continuity. We must decide how to store and manage conversation data to ensure statelessness while maintaining conversation context. This decision impacts system reliability, scalability, and user experience.

## Decision
We will implement direct database persistence (stateless model) using Neon Serverless PostgreSQL via SQLModel for storing conversation history. All conversation data (Conversations and Message entities) will be persisted directly to the database during each request cycle, ensuring no server-held state is maintained.

The persistence model will:
- Store Conversation records with session metadata (user_id, timestamps)
- Store Message records with user/assistant roles, content, and tool execution context
- Follow stateless architecture principles with no in-memory conversation state
- Use the same Neon DB as the task data for consistency and synchronization

## Alternatives
- **Client-side storage with periodic sync**: Store conversation history in browser storage with periodic synchronization to backend (potential data loss, limited cross-device access)
- **Server-side in-memory with database backup**: Hold conversation state in server memory with periodic database persistence (stateful, doesn't survive server restarts, scaling issues)
- **Hybrid model with caching layer**: Combine database persistence with Redis/Memcached for performance (increased complexity, cache invalidation issues)

## Consequences
**Positive:**
- Ensures conversation history survives server restarts and deployments
- Maintains statelessness, enabling horizontal scaling
- Provides reliable access to conversation history across sessions
- Synchronization between conversation and task data through shared database
- Consistent with overall stateless architecture approach

**Negative:**
- Increased database load with frequent read/write operations
- Potential performance impact from database round trips for each message
- Complexity in managing conversation history queries efficiently
- Need for pagination and history truncation mechanisms for long conversations

## References
- specs/2-todo-ai-chatbot/plan.md
- specs/2-todo-ai-chatbot/spec.md
- specs/2-todo-ai-chatbot/schema.md