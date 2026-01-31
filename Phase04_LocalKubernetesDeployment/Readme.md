# Taskify - Full-Stack Todo Web Application with AI Chatbot & Kubernetes Deployment

Taskify is a powerful, multi-user task management application built with modern web technologies. This project demonstrates a comprehensive full-stack implementation with advanced features including recurring tasks, priority management, beautiful UI/UX design, AI chatbot integration, and cloud-native deployment.

## 🚀 Project Overview

**Phase 2-4** of the Hackathon series, transitioning from a Phase 1 in-memory Python console app to a persistent, authenticated, responsive web application with a modern dashboard interface, enhanced with AI chatbot capabilities and deployed on local Kubernetes cluster.

### 🎯 Core Features
- **Multi-User Authentication**: Secure JWT-based authentication with user isolation
- **Task Management**: Complete CRUD operations with advanced features
- **Priority Levels**: HIGH, MEDIUM, LOW, NONE with color coding
- **Tagging System**: Multi-tag support for task categorization
- **Search & Filter**: Keyword search and advanced filtering capabilities
- **Sorting Options**: By priority, date, title, or due date
- **Recurring Tasks**: Daily, weekly, monthly patterns
- **Due Dates & Times**: DateTime precision with validation
- **Smart Reminders**: Browser notifications for due tasks
- **Responsive Design**: Mobile-first approach with desktop support
- **Dark Mode**: Theme toggle with smooth transitions
- **Glassmorphism UI**: Premium visual design with backdrop blur effects

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design system
- **Components**: shadcn/ui for production-ready components
- **Animations**: GSAP + Framer Motion for 60fps performance
- **Fonts**: JetBrains Mono (monospace), Inter (body text)
- **State Management**: React hooks, Context API, TanStack Query

### Backend
- **Language**: Python 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Package Manager**: UV
- **Authentication**: Better Auth with JWT tokens
- **Database**: Neon Serverless PostgreSQL

### AI Chatbot (Phase 3)
- **AI Framework**: OpenAI Agents SDK
- **Model Context Protocol (MCP)**: Official MCP SDK
- **LLM Provider**: OpenAI API (GPT-4 or later)
- **Chat UI**: OpenAI ChatKit
- **MCP Tools**: Standardized tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task)

### Kubernetes Deployment (Phase 4)
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes
- **Local Cluster**: Minikube
- **Packaging**: Helm
- **AI-Assisted DevOps**: Gordon for Docker, kubectl-ai and kagent for Kubernetes operations
- **CI/CD**: AI-assisted with Claude Code

### Deployment
- **Frontend**: Vercel
- **Backend**: Hugging Face Spaces
- **AI Chatbot**: OpenAI ChatKit (hosted) + MCP server on Hugging Face Spaces
- **Database**: Neon (serverless PostgreSQL)
- **Local Deployment**: Minikube (Kubernetes)

## 📋 Project Structure

```
Phase04_FullStackWebApp/
├── CLAUDE.md                           # Claude Code development rules
├── .specify/                           # Spec-Kit Plus configuration
├── .spec-kit/                          # Spec-Kit configuration
├── specs/                              # Feature specifications
│   ├── overview.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ai-chatbot/                     # Phase 3 AI Chatbot specifications
├── history/                            # Prompt History Records & ADRs
│   ├── prompts/
│   └── adr/
├── frontend/                           # Next.js application
│   ├── app/                            # App Router pages
│   ├── components/                     # Reusable React components
│   ├── context/                        # React Context providers
│   ├── hooks/                          # Custom React hooks
│   ├── lib/                            # Utilities and helpers
│   ├── public/                         # Static assets
│   ├── __tests__/                      # Test files
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── backend/                            # FastAPI application with MCP server
│   ├── app/
│   │   ├── agents/                     # Phase 3 AI agents
│   │   ├── config/
│   │   ├── database.py
│   │   ├── mcp/                        # Phase 3 Model Context Protocol
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── routes/
│   │   └── utils/
│   ├── main.py                         # FastAPI application entry point
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── tests/
├── helm/                               # Phase 4 Helm charts
│   └── todo-chatbot/                   # Todo Chatbot Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-secret.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── configmap.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── ingress.yaml
│           └── secret.yaml
├── scripts/                            # Phase 4 deployment scripts
│   ├── ai-operations.sh
│   ├── build-and-push.sh
│   ├── deploy.sh
│   ├── validation-tests.sh
│   └── placeholder.txt
├── docs/                               # Documentation
│   ├── containerization-blueprint.md
│   ├── deployment-template.md
│   ├── helm-blueprint.md
│   ├── k8s-skills.md
│   ├── lessons-learned.md
│   ├── subagent-configuration.md
│   └── troubleshooting.md
├── Readme.md                           # This file
├── Phase04_Guidance.md                 # Phase 4 specific guidance
└── Hackathon II - Todo Spec-Driven Development.pdf
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.13+ (for backend)
- PostgreSQL database (Neon recommended)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file with the following:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Create a `.env` file with the following:
```env
NEON_DB_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=your-super-secret-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
ALLOWED_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
```

5. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

## 📊 API Endpoints

### Authentication Endpoints
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Revoke JWT token
- `GET /api/auth/me` - Get current user info

### Task Endpoints
- `GET /api/{user_id}/tasks` - List user's tasks with filters
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion status

### User Profile Endpoints
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password

## 🎨 Design System

### Glassmorphism Effects
The UI features premium glassmorphism effects using:
- `bg-white/10` - Semi-transparent backgrounds
- `backdrop-blur-md` - Background blur effects
- `border border-white/20` - Subtle borders

### Color Palette
- **Primary**: Indigo/Purple gradients
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Danger**: Red (#EF4444)
- **Neutral**: Grayscale with dark mode support

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Adaptive layouts for all screen sizes

## 🔐 Security Features

- **JWT Authentication**: 7-day expiry with refresh capability
- **User Isolation**: Strict user data separation at database and API levels
- **Password Security**: bcrypt hashing with salt
- **Input Validation**: Comprehensive validation at all levels
- **SQL Injection Prevention**: Parameterized queries
- **CORS Configuration**: Proper origin restrictions
- **Rate Limiting**: Protection against brute force attacks

## 🧪 Testing

### Frontend Testing
- **Unit Tests**: Vitest with React Testing Library
- **Component Tests**: Shallow and integration testing
- **E2E Tests**: Playwright for critical user flows

### Backend Testing
- **Unit Tests**: pytest for business logic
- **Integration Tests**: API endpoint testing
- **Database Tests**: SQLModel integration tests

### Coverage Requirements
- Backend: 80%+ overall, 100% for auth/security
- Frontend: 70%+ overall, 90%+ for critical components
- E2E: 100% coverage for critical user flows

## 🚀 Deployment

### Phase 2-3: Traditional Deployment
#### Frontend Deployment (Vercel)
1. Connect your repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Backend API URL

#### Backend Deployment (Hugging Face Spaces)
1. Create a Space with Docker container option
2. Configure environment variables:
   - `NEON_DB_URL`: Database connection string
   - `JWT_SECRET`: JWT signing secret
   - `ALLOWED_ORIGINS`: Frontend domain

### Phase 4: Kubernetes Deployment (Local - Minikube)

#### Prerequisites
- Install Docker Desktop with Gordon AI enabled
- Install Minikube and start cluster: `minikube start`
- Install Helm 3.x

#### Containerization
1. Navigate to frontend: `cd frontend/`
2. Build frontend image: `docker build -t todo-frontend:latest .`
3. Navigate to backend: `cd ../backend/`
4. Build backend image: `docker build -t todo-backend:latest .`

#### Load Images to Minikube
```bash
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

#### Deploy with Helm
1. Navigate to Helm chart: `cd ../helm/todo-chatbot/`
2. Install chart: `helm install todo-app .`

#### Verify Deployment
```bash
kubectl get pods
kubectl get services
minikube service todo-app-todo-chatbot-frontend --url
```

### Environment Configuration
Update CORS in backend to include your production frontend URL:
```bash
ALLOWED_ORIGINS=["http://localhost:3000", "https://your-frontend.vercel.app", "http://192.168.49.2:32560"]
```

For Kubernetes deployment, the services are exposed via NodePorts or Ingress depending on your configuration.

## 📈 Features Roadmap

### Level 1: Basic CRUD (Foundation)
- ✅ User Authentication (signup, login, logout)
- ✅ Add Task with title and description
- ✅ View Tasks with status indication
- ✅ Update Task details
- ✅ Delete Task with confirmation
- ✅ Mark Complete/Incomplete toggle

### Level 2: Intermediate Features (Organization)
- ✅ Priority Levels (HIGH/MEDIUM/LOW/NONE)
- ✅ Tags/Categories system
- ✅ Search functionality
- ✅ Filter by status, priority, tags
- ✅ Sort by various criteria

### Level 3: Advanced Features (Intelligence)
- ✅ Recurring Tasks (DAILY/WEEKLY/MONTHLY)
- ✅ Due Dates & Times with validation
- ✅ Smart Reminders and notifications
- ✅ AI Chatbot Integration (natural language task management)
- ✅ MCP Tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task)
- ✅ Conversation history persistence
- ✅ Multi-language support (English and Urdu)

### Level 4: Cloud-Native Deployment
- ✅ Containerization with Docker
- ✅ Kubernetes orchestration with Minikube
- ✅ Helm chart packaging
- ✅ NodePort services for external access
- ✅ AI-assisted DevOps with Gordon, kubectl-ai, and kagent

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is part of the Hackathon series by Panaversity and follows the principles of Spec-Driven Development.

## 🙏 Acknowledgments

- [Panaversity](https://panaversity.org/) for organizing the Hackathon
- Next.js, FastAPI, and all the open-source libraries that made this project possible
- The Spec-Kit Plus framework for enabling Spec-Driven Development

---

**Project**: Multi-user Full-Stack Todo Web Application with AI Chatbot & Kubernetes Deployment
**Phase**: Phase 2-4 of 5 (Full-Stack Web Application + AI Chatbot Integration + Local Kubernetes Deployment)
**Technology**: Next.js 15+, FastAPI, SQLModel, Neon PostgreSQL, OpenAI Agents SDK, MCP, Kubernetes, Helm
**Architecture**: Strict Spec-Driven Development approach