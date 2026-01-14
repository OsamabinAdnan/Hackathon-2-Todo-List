---
name: improvement-suggestion
description: Advanced recommendations for code quality, scalability, security, and performance improvements in the Todo application. Focuses on optimizing Framer Motion usage for animations, enforcing token expiry, creating modular components, and aligning with hackathon judging criteria like clean architecture. Includes before/after pseudocode and rationale tied to project requirements. Use when (1) Optimizing code quality and maintainability across frontend/backend, (2) Improving scalability patterns (e.g., better Framer Motion usage for animations), (3) Enhancing security measures (e.g., token expiry enforcement, secure session management), (4) Creating modular, reusable components for better architecture, (5) Identifying performance optimizations (caching, database indexing, API efficiency), (6) Aligning implementation with hackathon judging criteria like clean architecture and best practices.
---

# Improvement Suggestion Skill

Advanced recommendations for enhancing code quality, scalability, security, and performance in the Todo application, with focus on clean architecture, maintainability, and hackathon judging criteria.

## Core Capabilities

### 1. Code Quality Improvements

Identify and suggest improvements for code quality:

**TypeScript/Next.js Quality Improvements:**
```typescript
// Before: Poor type safety and error handling
function getTask(id: any) {
  const response = fetch(`/api/tasks/${id}`);
  return response.data;
}

// After: Proper typing and error handling
interface Task {
  id: string;
  title: string;
  completed: boolean;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

async function getTask(id: string): Promise<Task> {
  try {
    const response = await fetch(`/api/tasks/${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch task: ${response.status}`);
    }

    const data = await response.json();
    return data as Task;
  } catch (error) {
    console.error('Error fetching task:', error);
    throw error;
  }
}
```

**Python/FastAPI Quality Improvements:**
```python
# Before: No type hints or validation
def create_task(title, description, user_id):
    task = Task(title=title, description=description, user_id=user_id)
    session.add(task)
    session.commit()
    return task

# After: Proper typing and validation
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Field, Session

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

def create_task(request: TaskCreateRequest, user_id: str, session: Session) -> Task:
    """
    Create a new task with proper validation and error handling.

    Args:
        request: Task creation request with validated data
        user_id: ID of the user creating the task
        session: Database session for the operation

    Returns:
        Created Task object

    Raises:
        ValueError: If input validation fails
        DatabaseError: If database operation fails
    """
    if not request.title.strip():
        raise ValueError("Task title cannot be empty")

    task = Task(
        title=request.title,
        description=request.description,
        completed=request.completed,
        user_id=user_id
    )

    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise DatabaseError(f"Failed to create task: {str(e)}")
```

### 2. Scalability Optimizations

**Framer Motion Animation Improvements:**
```typescript
// Before: Inefficient animations causing performance issues
import { motion } from 'framer-motion';

function TaskItem({ task }: { task: Task }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="task-card">
        <h3>{task.title}</h3>
        <p>{task.description}</p>
      </div>
    </motion.div>
  );
}

// After: Optimized animations with performance considerations
import { motion, AnimatePresence } from 'framer-motion';
import { useReducedMotion } from 'framer-motion';

function OptimizedTaskItem({ task }: { task: Task }) {
  const shouldReduceMotion = useReducedMotion();

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        damping: 25,
        stiffness: 300,
        duration: shouldReduceMotion ? 0 : 0.3
      }
    },
    exit: { opacity: 0, y: -20, scale: 0.95 }
  };

  return (
    <motion.div
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      whileTap={!shouldReduceMotion ? { scale: 0.98 } : {}}
      layout // Enable layout animations
      transition={{
        duration: shouldReduceMotion ? 0 : 0.2,
        type: "tween"
      }}
    >
      <div className="task-card">
        <h3>{task.title}</h3>
        <p>{task.description}</p>
      </div>
    </motion.div>
  );
}

// For lists of animated items
function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <AnimatePresence>
      {tasks.map(task => (
        <OptimizedTaskItem key={task.id} task={task} />
      ))}
    </AnimatePresence>
  );
}
```

**Database Scalability Improvements:**
```python
# Before: Inefficient queries without proper indexing
def get_user_tasks(user_id: str, completed: bool = None):
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    return session.exec(query).all()

# After: Optimized queries with proper indexing and pagination
from sqlmodel import select, desc
from typing import Optional, List, Tuple

def get_user_tasks_optimized(
    user_id: str,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "created_at",
    order_desc: bool = True
) -> Tuple[List[Task], int]:
    """
    Get user tasks with optimized query, filtering, and pagination.

    Args:
        user_id: ID of the user whose tasks to retrieve
        completed: Filter by completion status
        priority: Filter by priority level
        limit: Number of tasks to return
        offset: Number of tasks to skip
        order_by: Field to order by
        order_desc: Whether to order in descending order

    Returns:
        Tuple of (tasks list, total count)
    """
    # Build query with filters
    query = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority:
        query = query.where(Task.priority == priority)

    # Apply ordering
    if order_by == "created_at":
        query = query.order_by(desc(Task.created_at) if order_desc else Task.created_at)
    elif order_by == "title":
        query = query.order_by(desc(Task.title) if order_desc else Task.title)
    elif order_by == "due_date":
        query = query.order_by(desc(Task.due_date) if order_desc else Task.due_date)

    # Get total count for pagination
    count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    if completed is not None:
        count_query = count_query.where(Task.completed == completed)
    if priority:
        count_query = count_query.where(Task.priority == priority)

    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()
    return tasks, total

# Proper indexing in model definition
from sqlmodel import Field, SQLModel
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "completed"),
        Index("ix_tasks_user_priority", "user_id", "priority"),
        Index("ix_tasks_user_created_at", "user_id", "created_at"),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),
    )

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)  # Individual index
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="NONE", index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Security Enhancements

**Token Expiry and Session Management:**
```python
# Before: Basic JWT without proper expiry handling
from datetime import datetime, timedelta
import jwt

def create_token(user_id: str):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# After: Comprehensive token management with refresh tokens
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from sqlmodel import Session

class TokenManager:
    def __init__(self, access_token_secret: str, refresh_token_secret: str):
        self.access_token_secret = access_token_secret
        self.refresh_token_secret = refresh_token_secret
        self.access_token_expiry = timedelta(minutes=15)  # Short-lived access tokens
        self.refresh_token_expiry = timedelta(days=7)     # Longer-lived refresh tokens

    def create_access_token(self, user_id: str) -> str:
        """Create short-lived access token."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.access_token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, self.access_token_secret, algorithm='HS256')

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token and store in database."""
        token_hash = secrets.token_urlsafe(32)
        refresh_token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=datetime.utcnow() + self.refresh_token_expiry
        )

        # Store refresh token in database
        session.add(refresh_token)
        session.commit()

        return token_hash

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token and return payload if valid."""
        try:
            payload = jwt.decode(
                token,
                self.access_token_secret,
                algorithms=['HS256'],
                options={"verify_exp": True}
            )

            if payload.get('type') != 'access':
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str, user_id: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        # Verify refresh token exists and is not expired
        db_token = session.get(RefreshToken, refresh_token)
        if not db_token or db_token.expires_at < datetime.utcnow():
            return None

        # Revoke the used refresh token
        session.delete(db_token)
        session.commit()

        # Create new access token
        return self.create_access_token(user_id)

# Refresh token model
class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    token_hash: str = Field(unique=True, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field()

    # Relationship
    user: User = Relationship(back_populates="refresh_tokens")
```

### 4. Modular Component Architecture

**Frontend Component Improvements:**
```typescript
// Before: Monolithic component with mixed concerns
function TaskManager() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState('all');
  const [newTask, setNewTask] = useState('');

  // Mixed logic for data fetching, state management, and UI
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    // API call logic mixed with component logic
  };

  const addTask = async () => {
    // Task creation logic mixed with component logic
  };

  return (
    <div>
      {/* Complex JSX mixing presentation and logic */}
    </div>
  );
}

// After: Modular, reusable components with separation of concerns
// hooks/useTasks.ts
import { useState, useEffect } from 'react';

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  addTask: (task: Omit<Task, 'id'>) => Promise<void>;
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  filteredTasks: Task[];
  setFilter: (filter: string) => void;
}

export function useTasks(userId: string): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTasks();
  }, [userId]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/${userId}/tasks`);
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const addTask = async (taskData: Omit<Task, 'id'>) => {
    try {
      const response = await fetch(`/api/${userId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      const newTask = await response.json();
      setTasks([...tasks, newTask]);
    } catch (err) {
      setError('Failed to add task');
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'completed') return task.completed;
    if (filter === 'pending') return !task.completed;
    return true;
  });

  return {
    tasks,
    loading,
    error,
    addTask,
    updateTask: async () => {}, // Implementation omitted for brevity
    deleteTask: async () => {}, // Implementation omitted for brevity
    filteredTasks,
    setFilter
  };
}

// components/TaskForm.tsx
interface TaskFormProps {
  onSubmit: (task: Omit<Task, 'id'>) => void;
  loading?: boolean;
}

export function TaskForm({ onSubmit, loading }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, description, completed: false });
    setTitle('');
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Task description"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Adding...' : 'Add Task'}
      </button>
    </form>
  );
}

// components/TaskList.tsx
interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TaskList({ tasks, onToggle, onDelete }: TaskListProps) {
  return (
    <div className="task-list">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

// components/TaskItem.tsx
interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <motion.div className="task-item" layout>
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      <span className={task.completed ? 'completed' : ''}>
        {task.title}
      </span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </motion.div>
  );
}

// pages/tasks.tsx - Main page component
export default function TasksPage() {
  const {
    filteredTasks,
    loading,
    error,
    addTask,
    updateTask,
    deleteTask,
    setFilter
  } = useTasks(currentUser.id);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="tasks-page">
      <TaskForm onSubmit={addTask} />
      <FilterControls onFilterChange={setFilter} />
      <TaskList
        tasks={filteredTasks}
        onToggle={updateTask}
        onDelete={deleteTask}
      />
    </div>
  );
}
```

### 5. Performance Optimizations

**Backend Performance Improvements:**
```python
# Before: Synchronous, blocking operations
def get_user_dashboard_data(user_id: str):
    # Multiple sequential database calls
    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    completed_count = session.exec(
        select(func.count(Task.id))
        .where(Task.user_id == user_id)
        .where(Task.completed == True)
    ).one()
    overdue_tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.due_date < datetime.utcnow())
        .where(Task.completed == False)
    ).all()

    return {
        'tasks': tasks,
        'completed_count': completed_count,
        'overdue_tasks': overdue_tasks
    }

# After: Optimized with single query and eager loading
from sqlalchemy import func, case
from typing import Dict, Any

def get_user_dashboard_data_optimized(user_id: str) -> Dict[str, Any]:
    """
    Get user dashboard data with optimized single query approach.
    """
    # Single query with aggregated data
    stats_query = select(
        func.count(Task.id).label('total_tasks'),
        func.count(case((Task.completed == True, 1))).label('completed_count'),
        func.count(case((and_(Task.due_date < datetime.utcnow(), Task.completed == False), 1))).label('overdue_count')
    ).where(Task.user_id == user_id)

    stats_result = session.exec(stats_query).one()

    # Get recent tasks with proper pagination
    recent_tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .limit(10)
    ).all()

    return {
        'total_tasks': stats_result.total_tasks or 0,
        'completed_count': stats_result.completed_count or 0,
        'overdue_count': stats_result.overdue_count or 0,
        'recent_tasks': recent_tasks
    }

# Caching implementation
from functools import lru_cache
import time
from typing import Optional

class CachedTaskService:
    def __init__(self, cache_ttl: int = 300):  # 5 minutes TTL
        self.cache_ttl = cache_ttl
        self.cache = {}

    def _get_cache_key(self, user_id: str, filters: dict) -> str:
        return f"{user_id}:{hash(frozenset(filters.items()))}"

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        return time.time() - cache_entry['timestamp'] < self.cache_ttl

    def get_user_tasks_cached(
        self,
        user_id: str,
        filters: Optional[dict] = None
    ) -> List[Task]:
        if filters is None:
            filters = {}

        cache_key = self._get_cache_key(user_id, filters)

        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry):
                return cache_entry['data']

        # Fetch from database
        tasks = self._get_user_tasks_from_db(user_id, filters)

        # Store in cache
        self.cache[cache_key] = {
            'data': tasks,
            'timestamp': time.time()
        }

        return tasks

    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached data for a user."""
        keys_to_remove = [
            key for key in self.cache.keys()
            if key.startswith(f"{user_id}:")
        ]
        for key in keys_to_remove:
            del self.cache[key]

    def _get_user_tasks_from_db(self, user_id: str, filters: dict) -> List[Task]:
        """Internal method to fetch tasks from database."""
        query = select(Task).where(Task.user_id == user_id)

        for field, value in filters.items():
            if hasattr(Task, field):
                query = query.where(getattr(Task, field) == value)

        return session.exec(query).all()
```

### 6. Architecture Improvements

**Clean Architecture Patterns:**
```python
# Domain layer - Pure business logic
from abc import ABC, abstractmethod
from typing import Protocol, List, Optional

class Task(Protocol):
    id: str
    title: str
    description: Optional[str]
    completed: bool
    user_id: str

class TaskRepository(Protocol):
    async def create(self, task: Task) -> Task:
        ...

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        ...

    async def get_by_user(self, user_id: str) -> List[Task]:
        ...

    async def update(self, task_id: str, updates: dict) -> Optional[Task]:
        ...

    async def delete(self, task_id: str) -> bool:
        ...

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create_task(self, user_id: str, title: str, description: Optional[str] = None) -> Task:
        # Business logic validation
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        # Create task entity
        task = Task(
            id=str(uuid4()),
            title=title,
            description=description,
            completed=False,
            user_id=user_id
        )

        return await self.repository.create(task)

    async def get_user_tasks(self, user_id: str) -> List[Task]:
        return await self.repository.get_by_user(user_id)

# Infrastructure layer - Database implementation
from sqlmodel import Session, select
from typing import Dict, Any

class SQLTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self.session = session

    async def create(self, task: Task) -> Task:
        db_task = TaskModel.from_entity(task)
        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task.to_entity()

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        db_task = self.session.get(TaskModel, task_id)
        return db_task.to_entity() if db_task else None

    async def get_by_user(self, user_id: str) -> List[Task]:
        db_tasks = self.session.exec(
            select(TaskModel).where(TaskModel.user_id == user_id)
        ).all()
        return [task.to_entity() for task in db_tasks]

    async def update(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        db_task = self.session.get(TaskModel, task_id)
        if not db_task:
            return None

        for key, value in updates.items():
            setattr(db_task, key, value)

        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task.to_entity()

    async def delete(self, task_id: str) -> bool:
        db_task = self.session.get(TaskModel, task_id)
        if not db_task:
            return False

        self.session.delete(db_task)
        self.session.commit()
        return True

# API layer - FastAPI endpoints
from fastapi import Depends, HTTPException

async def get_task_service() -> TaskService:
    session = get_db_session()  # Dependency injection
    repository = SQLTaskRepository(session)
    return TaskService(repository)

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    try:
        task = await task_service.create_task(
            user_id=current_user.id,
            title=request.title,
            description=request.description
        )
        return TaskResponse.from_entity(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 7. Hackathon Judging Criteria Alignment

**Clean Architecture Implementation:**
```python
# Following SOLID principles
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Single Responsibility Principle
class TaskValidator:
    """Handles only task validation logic."""

    @staticmethod
    def validate_task_data(title: str, description: Optional[str] = None) -> bool:
        if not title or not title.strip():
            return False
        if len(title) > 200:
            return False
        if description and len(description) > 1000:
            return False
        return True

class TaskFormatter:
    """Handles only task formatting logic."""

    @staticmethod
    def format_task_for_response(task: Task) -> Dict[str, Any]:
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'user_id': task.user_id,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }

# Open/Closed Principle - Extendable notification system
class NotificationService(ABC):
    @abstractmethod
    async def send_notification(self, user_id: str, message: str):
        pass

class EmailNotificationService(NotificationService):
    async def send_notification(self, user_id: str, message: str):
        # Email-specific implementation
        pass

class PushNotificationService(NotificationService):
    async def send_notification(self, user_id: str, message: str):
        # Push notification-specific implementation
        pass

# Dependency Inversion - High-level modules depend on abstractions
class TaskNotificationService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    async def notify_task_created(self, user_id: str, task_title: str):
        message = f"New task created: {task_title}"
        await self.notification_service.send_notification(user_id, message)
```

### 8. Implementation Recommendations

**Before/After Comparison Framework:**
```python
class ImprovementAnalyzer:
    """Analyzes code and provides before/after improvement suggestions."""

    def __init__(self):
        self.improvement_patterns = {
            'type_safety': {
                'before': 'function process(data) { ... }',
                'after': 'function process(data: TaskData): ProcessedTask { ... }',
                'rationale': 'Improves type safety and reduces runtime errors'
            },
            'error_handling': {
                'before': 'const result = api.call(); return result;',
                'after': '''
try {
  const result = await api.call();
  return result;
} catch (error) {
  logger.error("API call failed:", error);
  throw new ApiError("Service unavailable");
}
                ''',
                'rationale': 'Provides proper error handling and logging'
            },
            'performance': {
                'before': 'tasks.map(task => expensiveOperation(task))',
                'after': '''
// Use memoization or debouncing for expensive operations
const processedTasks = useMemo(() =>
  tasks.map(task => expensiveOperation(task)),
  [tasks]
);
                ''',
                'rationale': 'Improves performance by preventing unnecessary recalculations'
            }
        }

    def analyze_file(self, file_path: str) -> List[Dict[str, str]]:
        """Analyze a file and return improvement suggestions."""
        suggestions = []

        with open(file_path, 'r') as f:
            content = f.read()

        for pattern_name, pattern_data in self.improvement_patterns.items():
            if self._detect_pattern(content, pattern_name):
                suggestions.append({
                    'pattern': pattern_name,
                    'before': pattern_data['before'],
                    'after': pattern_data['after'],
                    'rationale': pattern_data['rationale'],
                    'file': file_path,
                    'location': self._find_pattern_location(content, pattern_data['before'])
                })

        return suggestions

    def _detect_pattern(self, content: str, pattern_name: str) -> bool:
        """Detect if a pattern exists in the content."""
        # Implementation for pattern detection
        return True  # Simplified for example

    def _find_pattern_location(self, content: str, pattern: str) -> str:
        """Find the location of a pattern in the content."""
        # Implementation for location finding
        return "line 1-10"  # Simplified for example

# Usage example
analyzer = ImprovementAnalyzer()
suggestions = analyzer.analyze_file("frontend/components/TaskList.tsx")

for suggestion in suggestions:
    print(f"Pattern: {suggestion['pattern']}")
    print(f"Before:\n{suggestion['before']}")
    print(f"After:\n{suggestion['after']}")
    print(f"Rationale: {suggestion['rationale']}")
    print(f"Location: {suggestion['location']}")
    print("-" * 50)
```

## Usage Examples

### Example 1: Code Quality Enhancement
```
User: "Improve the type safety in the Task API endpoints"
Agent: [Triggers improvement-suggestion skill] → Analyzes backend API code, identifies missing type hints, suggests before/after improvements with proper Pydantic models and validation, provides rationale for maintainability
```

### Example 2: Performance Optimization
```
User: "Optimize Framer Motion animations in the dashboard"
Agent: [Triggers improvement-suggestion skill] → Reviews animation code, suggests performance optimizations with reduced motion support, provides before/after examples with rationale for 60fps target
```

### Example 3: Security Enhancement
```
User: "Improve token expiry handling in the auth system"
Agent: [Triggers improvement-suggestion skill] → Analyzes JWT implementation, suggests refresh token system with proper database storage, provides comprehensive before/after code with security rationale
```

### Example 4: Architecture Improvement
```
User: "Make the components more modular and reusable"
Agent: [Triggers improvement-suggestion skill] → Reviews component structure, suggests separation of concerns with custom hooks, provides before/after examples with clean architecture principles
```

## Quality Checklist

- [ ] Code quality improvements follow TypeScript/Python best practices
- [ ] Scalability optimizations include proper indexing and pagination
- [ ] Security enhancements include token management and validation
- [ ] Modular components follow separation of concerns
- [ ] Performance optimizations consider user experience
- [ ] Architecture follows clean design principles (SOLID, DRY, KISS)
- [ ] Improvements align with hackathon judging criteria
- [ ] Before/after examples are clear and actionable
- [ ] Rationale explains the benefits of each improvement
- [ ] Suggestions are practical and implementable

## Integration Points

- **Code Review Process**: Provides improvement suggestions during reviews
- **Development Workflow**: Integrated into pull request review process
- **Testing Framework**: Suggests test cases for improved code
- **CI/CD Pipeline**: Automated quality checks and suggestions
- **Documentation**: Updates documentation to reflect improvements

## References

- **Architecture Overview**: `@specs/overview.md` for project architecture principles
- **Security Guidelines**: `@specs/features/authentication.md` for authentication and security requirements
- **API Design**: `@specs/api/rest-endpoints.md` for API improvement patterns
- **Database Schema**: `@specs/database/schema.md` for data architecture
- **Frontend Guidelines**: `@specs/ui/design-system.md` for component architecture
- **Testing Guidelines**: `@specs/testing/overview.md` for quality improvement patterns
- **Performance Patterns**: `@specs/ui/animations.md` for performance optimization techniques
- **Accessibility**: `@specs/ui/accessibility.md` for inclusive design improvements
- **Responsive Design**: `@specs/ui/responsive-design.md` for cross-device compatibility
- **Dashboard Layout**: `@specs/ui/dashboard-layout.md` for UI structure improvements
- **Glassmorphism**: `@specs/ui/glassmorphism.md` for visual design enhancements
- **Dark Mode**: `@specs/ui/dark-mode.md` for theme implementation
- **Backend Testing**: `@specs/testing/backend-testing.md` for server-side quality
- **Frontend Testing**: `@specs/testing/frontend-testing.md` for client-side quality
- **E2E Testing**: `@specs/testing/e2e-testing.md` for integration testing
- **Task CRUD**: `@specs/features/task-crud.md` for feature-specific improvements