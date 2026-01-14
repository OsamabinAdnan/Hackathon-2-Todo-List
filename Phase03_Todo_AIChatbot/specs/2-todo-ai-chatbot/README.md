# Phase 3: AI-Powered Todo Chatbot Integration

## Overview

Phase 3 extends the Phase 2 multi-user Todo web application with an AI-powered chatbot that enables natural language task management. Using OpenAI ChatKit, FastAPI, OpenAI Agents SDK, Official MCP SDK, and Neon PostgreSQL, users can manage their tasks through conversational AI while maintaining the same security model as the existing application.

### Key Features
- Natural language task management (create, list, update, delete, complete)
- Seamless integration with existing Phase 2 authentication and data
- State-of-the-art AI agent with MCP tool integration
- Conversation history persistence and context management
- Multilingual support (English and Urdu for Phase 3 bonus feature)
- Enterprise-grade security with user isolation
- Responsive UI with consistent design system

### Technologies Used
- **Frontend**: OpenAI ChatKit (hosted)
- **Backend**: FastAPI + OpenAI Agents SDK + Official MCP SDK
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT tokens)
- **ORM**: SQLModel
- **Deployment**: Hugging Face Spaces (MCP server), OpenAI hosting (ChatKit UI)

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatKit UI    │◄──►│   FastAPI       │◄──►│   OpenAI        │
│   (Hosted by    │    │   Chat Endpoint │    │   Agent SDK     │
│   OpenAI)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                           │
                              ▼                           ▼
                    ┌─────────────────┐         ┌─────────────────┐
                    │   Neon         │         │   MCP Tools     │
                    │   PostgreSQL    │         │   (add_task,    │
                    │                 │         │   list_tasks,   │
                    │  • users        │         │   complete_task,│
                    │  • tasks        │         │   delete_task,  │
                    │  • conversations│         │   update_task)  │
                    │  • messages     │         └─────────────────┘
                    └─────────────────┘                  │
                                                         ▼
                                                ┌─────────────────┐
                                                │   Phase 2       │
                                                │   Integration   │
                                                │                 │
                                                │  • Authentication│
                                                │  • User Isolation│
                                                │  • Task Data    │
                                                └─────────────────┘
```

### Key Design Patterns

1. **Stateless Architecture**: Server maintains no session state; all conversation history stored in database
2. **MCP Tool Integration**: AI agent interacts with system through standardized MCP tools
3. **User Isolation**: All operations scoped to authenticated user via JWT validation
4. **Event Sourcing**: Conversation history preserved as immutable message log
5. **API Gateway Pattern**: Single entry point with authentication and rate limiting

## Getting Started

### Prerequisites

- Python 3.13+ (for backend)
- Node.js 18+ (for frontend tools)
- OpenAI API access
- Neon PostgreSQL database
- Better Auth configuration from Phase 2

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Phase02_FullStackWebApp
   ```

2. **Set up Phase 2 prerequisites** (ensure Phase 2 is fully functional):
   - Database connection established
   - Better Auth configured
   - Phase 2 backend running

3. **Configure environment variables**:
   ```bash
   # In backend/.env
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://user:pass@ep-xxxx.neon.tech/dbname
   BETTER_AUTH_SECRET=your_jwt_secret_from_phase2
   ```

4. **Install backend dependencies**:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   ```

5. **Apply database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start the MCP server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

### Configuration

#### OpenAI ChatKit Setup

1. Deploy your MCP server to Hugging Face Spaces
2. Obtain your server endpoint URL
3. Configure ChatKit to connect to your endpoint
4. Add your domain to OpenAI's allowlist for production use

#### MCP Server Configuration

The MCP server is configured through environment variables in `backend/.env`:

```bash
# OpenAI API
OPENAI_API_KEY=your_api_key

# Database
DATABASE_URL=your_neon_connection_string

# Authentication (must match Phase 2)
BETTER_AUTH_SECRET=your_secret

# Rate limiting
CHAT_RATE_LIMIT_PER_MINUTE=100
MCP_TOOL_RATE_LIMIT_ADD_TASK=100
MCP_TOOL_RATE_LIMIT_LIST_TASKS=500
MCP_TOOL_RATE_LIMIT_COMPLETE_TASK=100
MCP_TOOL_RATE_LIMIT_DELETE_TASK=50
MCP_TOOL_RATE_LIMIT_UPDATE_TASK=100
```

## Specification Documents

All implementation follows these specification documents:

- **Feature Specification**: `@specs/2-todo-ai-chatbot/spec.md`
- **API Contracts**: `@specs/2-todo-ai-chatbot/contracts.md`
- **Database Schema**: `@specs/2-todo-ai-chatbot/schema.md`
- **MCP Tools**: `@specs/api/mcp-tools.md`
- **Implementation Checklist**: `@specs/2-todo-ai-chatbot/checklist.md`
- **Research**: `@specs/2-todo-ai-chatbot/research.md`
- **Quick Start**: `@specs/2-todo-ai-chatbot/quickstart.md`

## Usage

### Natural Language Commands

The AI chatbot understands various natural language patterns:

#### Task Creation
- "Add a task to buy groceries"
- "Create a task called 'Prepare presentation'"
- "I need to schedule a meeting with the team"
- "Remember to call the doctor tomorrow"

#### Task Listing
- "Show me my tasks"
- "What's on my list?"
- "Show me pending tasks"
- "What have I completed?"

#### Task Completion
- "Mark 'Buy groceries' as complete"
- "Complete the meeting task"
- "Finish the presentation task"
- "I'm done with the shopping task"

#### Task Deletion
- "Delete the old task"
- "Remove the meeting from tomorrow"
- "Cancel the appointment task"

#### Task Updates
- "Change 'Grocery shopping' to 'Weekly grocery shopping'"
- "Make the presentation task high priority"
- "Update the meeting time to 3 PM"

### API Endpoints

#### Chat Endpoint
```
POST /api/{user_id}/chat
Authorization: Bearer <jwt_token>

Request:
{
  "conversation_id": "optional-uuid",
  "message": "natural language command",
  "timestamp": "optional-iso-timestamp"
}

Response:
{
  "conversation_id": "uuid",
  "response": "ai response text",
  "tool_calls": [...],
  "trace_id": "uuid",
  "timestamp": "iso-timestamp"
}
```

## Security

### Authentication & Authorization
- JWT tokens validated on every request
- User ID extracted and verified against token claims
- All operations scoped to authenticated user
- Cross-user access prevented with 403 responses

### Data Protection
- All database queries filtered by user_id
- MCP tools validate user ownership before operations
- No exposure of other users' data in error messages
- Encrypted connections to database

### Rate Limiting
- 100 requests per minute per user for chat endpoint
- Per-tool rate limits for MCP operations
- 429 responses with retry-after headers

## Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Specific test categories
pytest tests/test_chat.py          # Chat endpoint tests
pytest tests/test_mcp_tools.py     # MCP tool tests
pytest tests/test_auth.py          # Authentication tests
pytest tests/test_security.py      # Security tests
```

### Test Coverage Requirements
- Backend: 80%+ overall coverage
- Security/Authentication: 100% coverage
- MCP Tools: 90%+ coverage
- Agent Behavior: 80%+ coverage

## Deployment

### MCP Server Deployment
1. Deploy to Hugging Face Spaces using the FastAPI app
2. Configure environment variables in the deployment
3. Ensure database connection is available
4. Test endpoint accessibility

### ChatKit UI Configuration
1. Add your MCP server endpoint to ChatKit configuration
2. Configure domain allowlist for production
3. Set up custom styling to match Phase 2 theme
4. Test conversation functionality

### Environment Variables for Production
```bash
# Database (production)
DATABASE_URL=production_neon_url

# OpenAI API (production)
OPENAI_API_KEY=prod_api_key

# Authentication (must match Phase 2)
BETTER_AUTH_SECRET=prod_secret

# Security
SECURE_SSL_REDIRECT=true
DEBUG=false
ALLOWED_HOSTS=your-domain.com,your-hf-space-url.hf.space
```

## Development Workflow

### Spec-Driven Development
1. Review specifications in `@specs/2-todo-ai-chatbot/`
2. Write failing tests following TDD principles
3. Implement minimal code to pass tests
4. Refactor while keeping tests green
5. Create PHRs for all interactions

### Key Commands
```bash
# Generate PHR for current work
.sp phr

# Run linting
cd backend && ruff check .
cd backend && ruff format .

# Run tests
cd backend && pytest

# Check test coverage
cd backend && pytest --cov=app --cov-report=html
```

## Integration with Phase 2

### Authentication Integration
- Reuses Better Auth JWT tokens from Phase 2
- Same user isolation model applied
- Consistent error response formats
- Shared database schema for users and tasks

### Data Consistency
- Same task data model used by MCP tools
- User IDs consistent between both phases
- Shared database transactions when needed
- Consistent validation rules

## Performance

### Benchmarks
- Chat response time: <3 seconds (95th percentile)
- MCP tool execution: <100ms average
- Database query time: <50ms average
- Agent execution timeout: 30 seconds

### Optimization Strategies
- Database connection pooling
- Query optimization with proper indexing
- Conversation history truncation
- Efficient token management

## Contributing

### Development Guidelines
1. Follow Spec-Driven Development approach
2. Write tests before implementation code
3. Maintain 100% user isolation
4. Use consistent error response formats
5. Follow established code patterns from Phase 2

### Code Review Checklist
- [ ] Specifications followed correctly
- [ ] Security requirements met
- [ ] User isolation enforced
- [ ] Tests cover all functionality
- [ ] Error handling comprehensive
- [ ] Performance requirements met

## Troubleshooting

### Common Issues

1. **JWT Authentication Failures**
   - Verify `BETTER_AUTH_SECRET` matches Phase 2
   - Check token format and expiration
   - Ensure user_id in token matches request parameter

2. **MCP Tool Access Issues**
   - Verify tool schemas follow MCP specification
   - Check user_id validation in all tools
   - Confirm database permissions

3. **Conversation History Problems**
   - Verify database indexes for performance
   - Check conversation/message relationships
   - Ensure chronological ordering

4. **OpenAI API Errors**
   - Confirm API key validity
   - Check rate limits
   - Verify model availability

### Debugging Tips
- Enable detailed logging with `LOG_LEVEL=DEBUG`
- Use trace_id for request correlation
- Check database directly for conversation state
- Monitor API usage quotas

## Roadmap

### Phase 4 Integration Plans
- Kubernetes deployment patterns
- Enhanced analytics and insights
- Advanced collaboration features
- Mobile application integration

### Future Enhancements
- Voice input/output capabilities
- Advanced natural language understanding
- Machine learning-powered task suggestions
- Integration with calendar applications

## Support

### Documentation
- Primary specifications in `@specs/2-todo-ai-chatbot/`
- API documentation via OpenAPI/Swagger
- Database schema documentation
- Deployment guides

### Contact
- Development team: [team-email]
- Issue tracking: [issue-tracker-url]
- Real-time support: [chat-channel]

---

**Version**: 1.0.0
**Phase**: 3 of 5
**Created**: 2026-01-13
**Status**: Under Development