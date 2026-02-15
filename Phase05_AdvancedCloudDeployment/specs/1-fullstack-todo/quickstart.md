# Quickstart Guide: Multi-User Full-Stack Todo Web Application

## Prerequisites

### System Requirements
- Node.js 18+ (for frontend development)
- Python 3.13+ (for backend development)
- UV Package Manager (for Python dependencies)
- PostgreSQL client (for database operations)
- Git
- A terminal/shell environment

### Development Environment Setup
For Windows users: Use WSL 2 (Windows Subsystem for Linux) for optimal development experience

## Initial Setup

### 1. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd Phase02_FullStackWebApp
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your database and auth secrets
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your API URLs and other configuration
```

## Environment Configuration

### Backend (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
NEON_DATABASE_URL=your_neon_connection_string

# Authentication
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
# Generate with: openssl rand -base64 32

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend (.env)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000

# Development
NEXT_PUBLIC_DEBUG=true
```

## Database Setup

### 1. PostgreSQL Setup
```bash
# Start PostgreSQL server (if not already running)
# Create database
createdb todo_app

# Or if using Neon
# Create a new project in Neon dashboard and get the connection string
```

### 2. Run Initial Migrations (when available)
```bash
# In backend directory
cd backend
source .venv/bin/activate

# Initial database setup will be handled by the application
# SQLModel will create tables automatically in development
```

## Running the Application

### 1. Start Backend Server
```bash
# In backend directory
cd backend
source .venv/bin/activate

# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend Server
```bash
# In frontend directory
cd frontend

# Run the development server
npm run dev
```

### 3. Application URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs

## Development Commands

### Backend Commands
```bash
# Run backend with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
ruff format .
ruff check . --fix

# Install new dependencies
uv pip install package-name
```

### Frontend Commands
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint

# Run formatting
npm run format

# Install new dependencies
npm install package-name
```

## API Testing

### Using the API Documentation
1. Start the backend server
2. Navigate to http://localhost:8000/docs
3. Use the interactive API documentation to test endpoints

### Example API Call
```bash
# Create a user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Password123!"}'

# Get user tasks (after authentication)
curl -X GET http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Common Tasks

### 1. Adding a New Feature
1. Create a new spec file in `specs/feature-name/spec.md`
2. Run `/sp.clarify` to resolve ambiguities
3. Run `/sp.plan` to create implementation plan
4. Run `/sp.tasks` to break into testable tasks
5. Follow TDD: Write failing test first (`/sp.red`)
6. Implement minimal code to pass test (`/sp.green`)
7. Refactor while keeping tests green (`/sp.refactor`)

### 2. Running Tests
```bash
# Backend tests
cd backend
source .venv/bin/activate
pytest

# Frontend tests
cd frontend
npm run test
```

### 3. Checking Test Coverage
```bash
# Backend coverage (should be 80%+ overall, 100% for auth/security)
cd backend
source .venv/bin/activate
pytest --cov=app --cov-report=html

# Frontend coverage (should be 70%+ overall, 90%+ for critical components)
cd frontend
npm run test:coverage
```

## Troubleshooting

### Common Issues

#### Backend won't start
- Ensure virtual environment is activated: `source .venv/bin/activate`
- Check that all dependencies are installed: `uv pip install -r requirements.txt`
- Verify environment variables are set correctly

#### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check that `NEXT_PUBLIC_API_URL` in frontend `.env` matches backend URL
- Ensure CORS is configured correctly in backend

#### Database connection issues
- Verify PostgreSQL is running
- Check that `DATABASE_URL` in backend `.env` is correct
- Ensure database exists and is accessible

### Development Tips
- Always run tests before committing code
- Follow TDD: Red → Green → Refactor cycle
- Use meaningful commit messages that reference the feature being implemented
- Keep PRs small and focused on a single feature or bug fix

## Deployment

### Frontend Deployment
- For Vercel: Connect repository and deploy automatically
- For GitHub Pages: Run `npm run build` and deploy the `out` directory

### Backend Deployment
- For Hugging Face Spaces: Use the Space template with the provided configuration
- Ensure environment variables are set in the deployment environment

### Database Deployment
- For Neon: Use the production connection string in deployment environment
- Ensure proper backup and scaling settings are configured