# Todo AI Chatbot (Phase-3) - Specification

## Overview
This document specifies the implementation of the Todo AI Chatbot for Phase 3. The system extends the existing Todo application with a conversational AI interface that allows users to manage their tasks through natural language interactions. The implementation follows a spec-driven approach with Claude Code.

## Phase 3: Todo AI Chatbot Integration

### Objective
Create a conversational interface that allows users to manage their todo tasks using natural language. The AI chatbot will integrate with the existing Phase 2 backend and database while maintaining all existing functionality.

### Core Requirements
1. **Natural Language Processing**: Users can create, update, delete, and query tasks using natural language
2. **MCP Tools Integration**: AI agent uses MCP tools for all database operations
3. **Stateless Architecture**: Server maintains no conversation state; all state persisted to database
4. **Security Preservation**: Maintains same user isolation and authentication as Phase 2
5. **UI Consistency**: Chat interface matches existing app theme and design system

### Technical Architecture

#### Frontend Components
- **Chat Interface**: OpenAI ChatKit UI component
- **Theme Consistency**: Matches existing dashboard theme (dark mode, glassmorphism, colors)
- **Authentication**: JWT token passed to chat requests
- **Layout**: Integrated into existing dashboard layout alongside task management UI

#### Backend Components
- **MCP Server**: Exposes todo operations as standardized tools
- **AI Agent**: OpenAI Agent SDK with conversation memory
- **Database**: Neon PostgreSQL with conversation/message tables
- **Authentication**: JWT-based, same as Phase 2

#### MCP Tools Specification
The MCP server will expose these standardized tools:

**add_task(user_id, title, description)**
- Creates a new task for the specified user
- Returns task_id, status, and title

**list_tasks(user_id, status="all")**
- Lists tasks for the specified user with optional status filter
- Returns array of task objects

**complete_task(user_id, task_id)**
- Marks a task as complete for the specified user
- Returns task_id, status, and title

**update_task(user_id, task_id, title, description)**
- Updates task title and/or description for the specified user
- Returns task_id, status, and title

**delete_task(user_id, task_id)**
- Deletes a task for the specified user
- Returns task_id, status, and title

### Database Extensions

#### New Tables
**conversations**
- id (UUID, primary key)
- user_id (UUID, foreign key to users)
- created_at (timestamp)
- updated_at (timestamp)

**messages**
- id (UUID, primary key)
- user_id (UUID, foreign key to users)
- conversation_id (UUID, foreign key to conversations)
- role (string: "user" or "assistant")
- content (text)
- tool_calls (JSON)
- created_at (timestamp)

#### Existing Table Integration
The AI chatbot will use the existing `tasks` and `users` tables from Phase 2, maintaining all security and isolation patterns.

### User Interaction Flow
1. User sends natural language message to chat endpoint
2. System retrieves conversation history from database
3. AI agent processes message and invokes appropriate MCP tools
4. Tools execute database operations with user validation
5. Assistant response is stored in database
6. Response is returned to user

### Security Requirements
- All MCP tools validate user_id matches authenticated user
- Users can only access their own conversations and tasks
- JWT authentication required for all chat endpoints
- Same security model as Phase 2 maintained

### Success Criteria
- [ ] Users can add tasks via natural language (e.g., "Add a task to buy groceries")
- [ ] Users can list tasks via natural language (e.g., "Show me my tasks")
- [ ] Users can complete tasks via natural language (e.g., "Mark task 1 as complete")
- [ ] Users can update tasks via natural language (e.g., "Update task 1 to 'Call mom'")
- [ ] Users can delete tasks via natural language (e.g., "Delete the meeting task")
- [ ] Conversation history persists across sessions
- [ ] User isolation maintained (users can't access others' tasks/conversations)
- [ ] Chat UI matches existing app theme and design
- [ ] All existing Phase 2 functionality remains intact
- [ ] Server stateless with all state in database

### Performance Requirements
- [ ] Chat response time < 2 seconds
- [ ] MCP tool execution time < 500ms
- [ ] Database operations < 200ms
- [ ] JWT validation < 10ms

### Error Handling
- [ ] Graceful handling of invalid natural language
- [ ] Proper error messages when tasks don't exist
- [ ] Authentication failures return 401
- [ ] Cross-user access attempts return 403
- [ ] Tool execution failures handled gracefully

### Testing Requirements
- [ ] 100% test coverage for chat endpoint
- [ ] 100% test coverage for security (user isolation)
- [ ] MCP tool functionality tests
- [ ] Natural language processing tests
- [ ] Conversation persistence tests
- [ ] Error handling tests

## Implementation Approach

### Phase 1: MCP Server Setup
- [ ] Set up MCP server infrastructure
- [ ] Implement MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- [ ] Add user validation to all tools
- [ ] Test MCP tool functionality

### Phase 2: AI Agent Configuration
- [ ] Set up OpenAI Agent SDK
- [ ] Configure agent with MCP tools
- [ ] Implement conversation memory
- [ ] Test agent responses

### Phase 3: Backend API
- [ ] Implement chat endpoint POST /api/{user_id}/chat
- [ ] Add JWT authentication to chat endpoint
- [ ] Implement conversation history retrieval
- [ ] Store user and assistant messages
- [ ] Return structured responses with tool calls

### Phase 4: Frontend Integration
- [ ] Install ChatKit dependencies
- [ ] Configure ChatKit component with backend endpoint
- [ ] Style ChatKit to match existing theme
- [ ] Attach JWT token to chat requests
- [ ] Integrate chat UI into dashboard layout

### Phase 5: Validation and Testing
- [ ] Test all chatbot functionalities
- [ ] Validate security requirements
- [ ] Performance testing
- [ ] User acceptance testing

## Dependencies
- Phase 2 backend and database must be operational
- OpenAI API key for agent functionality
- MCP SDK for tool integration
- Existing authentication system

## Constraints
- All existing Phase 2 functionality must remain intact
- No manual coding; all implementation via Claude Code
- Spec-driven development approach
- Security model from Phase 2 maintained
- UI consistency with existing design system

## Acceptance Tests
- [ ] Natural language task creation works
- [ ] Natural language task listing works
- [ ] Natural language task completion works
- [ ] Natural language task updates work
- [ ] Natural language task deletion works
- [ ] Conversation history persists
- [ ] User isolation maintained
- [ ] Theme consistency achieved
- [ ] Performance requirements met
- [ ] Error handling works properly

## Success Metrics
- [ ] 90%+ success rate for natural language understanding
- [ ] <2 second response time for chat interactions
- [ ] 100% user isolation (no cross-user access)
- [ ] Zero regression in Phase 2 functionality
- [ ] 100% test coverage for new features