from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from app.config.settings import settings
from app.database import init_db
import uvicorn

# Import routers
from app.routes import auth, tasks, users, chat

app = FastAPI(
    title="Taskify API",
    description="Powerful multi-user task management application with JWT authentication, recurring tasks, and advanced features",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/", summary="API information", description="Get API information and available endpoints")
async def root():
    return {
        "message": "Taskify API",
        "description": "Powerful multi-user task management application with JWT authentication, recurring tasks, and advanced features",
        "version": "2.0.0",
        "endpoints": {
            "/": "API information and available endpoints (this endpoint)",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)",
            "/api/auth/signup": "POST endpoint to register a new user account",
            "/api/auth/login": "POST endpoint to authenticate user with email/password",
            "/api/auth/logout": "POST endpoint to end current user session (client-side token cleanup)",
            "/api/users/me": "GET endpoint to get current authenticated user information (requires JWT token)",
            "/api/users/me": "DELETE endpoint to delete current user account (requires JWT token)",
            "/api/users/me": "PATCH endpoint to update current user profile (requires JWT token)",
            "/api/{user_id}/tasks": "GET endpoint to retrieve all tasks with filtering, sorting, and pagination (requires JWT token)",
            "/api/{user_id}/tasks": "POST endpoint to create a new task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "GET endpoint to retrieve a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "PUT endpoint to update a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}": "DELETE endpoint to delete a specific task (requires JWT token)",
            "/api/{user_id}/tasks/{task_id}/complete": "PATCH endpoint to toggle task completion status (requires JWT token)",
            "/api/{user_id}/chat": "POST endpoint to send messages and get AI responses (requires JWT token)",
            "/api/{user_id}/conversations/{conversation_id}/messages": "GET endpoint to retrieve conversation history (requires JWT token)",
            "/api/{user_id}/conversations": "POST endpoint to create a new conversation (requires JWT token)",
            "/api/{user_id}/conversations": "GET endpoint to list all user's conversations (requires JWT token)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
