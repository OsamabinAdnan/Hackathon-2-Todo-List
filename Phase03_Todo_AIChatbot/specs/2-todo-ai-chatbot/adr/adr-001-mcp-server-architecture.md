# ADR-001: MCP Server Architecture

## Status
Proposed

## Date
2026-01-13

## Context
The system requires AI-powered task management through natural language processing. We need to decide how to architect the Model Context Protocol (MCP) tools that will enable the AI agent to perform task operations. The decision impacts how the AI agent will interact with task data, how security will be handled across services, and how the system will scale.

## Decision
We will implement a separate MCP server using the Official MCP SDK that exposes task operations as tools to the AI agent. This MCP server will operate independently from the FastAPI backend but will share access to the same Neon PostgreSQL database.

The MCP server will:
- Expose stateless tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task)
- Directly query/modify the same Neon DB as the FastAPI backend using SQLModel
- Enforce user isolation by validating user_id for all operations
- Maintain complete separation of concerns from the orchestration layer

## Alternatives
- **Integrated MCP tools within FastAPI backend**: Embed MCP tools directly in the FastAPI application, reducing service count but mixing concerns
- **Cloud-based MCP service**: Use a cloud-hosted MCP solution for easier deployment but less control
- **Direct database access from agent**: Allow the AI agent to access the database directly without MCP tools (security risk)

## Consequences
**Positive:**
- Clear separation of concerns between orchestration (FastAPI) and tool execution (MCP server)
- Independent scaling of MCP server based on AI usage patterns
- Follows MCP best practices and standard patterns
- Enhanced security through explicit tool contracts
- Easier testing and maintenance of individual components

**Negative:**
- Increased complexity with additional service to deploy and monitor
- Additional network hop between FastAPI and MCP server
- More complex debugging when issues span multiple services
- Additional configuration and deployment overhead

## References
- specs/2-todo-ai-chatbot/plan.md
- specs/2-todo-ai-chatbot/spec.md
- specs/2-todo-ai-chatbot/mcp-tools.md