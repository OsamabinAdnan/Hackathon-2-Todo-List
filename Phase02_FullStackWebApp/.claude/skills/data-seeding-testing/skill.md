---
name: data-seeding-testing
description: Provide scripts to seed test data (e.g., sample tasks with tags) and run unit tests for CRUD operations, validating multi-user isolation. Use when (1) Creating test data for development or demo purposes, (2) Need pytest fixtures for database testing, (3) Writing unit tests for CRUD operations, (4) Validating multi-user data isolation (tasks belong to correct users), (5) Creating factory functions for generating realistic test data, (6) Preparing demo data for video submission or presentations, (7) Testing database migrations with sample data.
---
# Data Seeding and Testing Skill

Create and manage test data for the Todo application, including sample data generation, pytest fixtures, and comprehensive testing for CRUD operations with multi-user isolation validation.

## Core Capabilities

### 1. Test Data Generation

**Creating Sample Data for Development:**
```python
import uuid
from datetime import datetime, timedelta
from typing import List
from app.models.user import User
from app.models.task import Task, Priority
from app.utils.security import hash_password

def create_sample_users() -> List[dict]:
    """Generate sample user data for seeding."""
    return [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@example.com",
            "password_hash": hash_password("SecurePass123!"),
            "name": "Admin User",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "user1@example.com",
            "password_hash": hash_password("UserPass456!"),
            "name": "Regular User 1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "user2@example.com",
            "password_hash": hash_password("UserPass789!"),
            "name": "Regular User 2",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

def create_sample_tasks_for_user(user_id: str) -> List[dict]:
    """Generate sample task data for a specific user."""
    base_time = datetime.utcnow()
    return [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Complete project proposal",
            "description": "Write and review the quarterly project proposal document",
            "completed": False,
            "priority": Priority.HIGH,
            "tags": ["work", "important", "deadline"],
            "due_date": base_time + timedelta(days=3),
            "is_recurring": False,
            "created_at": base_time - timedelta(hours=1),
            "updated_at": base_time - timedelta(hours=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, fruits",
            "completed": True,
            "priority": Priority.MEDIUM,
            "tags": ["personal", "shopping"],
            "due_date": base_time - timedelta(days=1),
            "is_recurring": False,
            "created_at": base_time - timedelta(days=2),
            "updated_at": base_time - timedelta(days=1),
            "completed_at": base_time - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Schedule team meeting",
            "description": "Coordinate with team members for next week's planning",
            "completed": False,
            "priority": Priority.MEDIUM,
            "tags": ["work", "meeting"],
            "due_date": base_time + timedelta(days=1),
            "is_recurring": False,
            "created_at": base_time - timedelta(hours=2),
            "updated_at": base_time - timedelta(hours=2)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Learn new framework",
            "description": "Spend 2 hours learning the new React patterns",
            "completed": False,
            "priority": Priority.LOW,
            "tags": ["learning", "development"],
            "due_date": base_time + timedelta(days=7),
            "is_recurring": True,
            "recurrence_pattern": "WEEKLY",
            "created_at": base_time - timedelta(hours=3),
            "updated_at": base_time - timedelta(hours=3)
        }
    ]
```

**Data Seeding Script:**
```python
# scripts/seed_data.py
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.models.task import Task
from app.utils.security import hash_password

def seed_database():
    """Seed the database with sample data."""
    print("Seeding database with sample data...")

    with Session(engine) as session:
        # Check if data already exists
        user_count = session.exec(select(User)).count()
        if user_count > 0:
            print("Database already has data. Skipping seeding.")
            return

        # Create sample users
        from app.models.user import User
        users_data = [
            User(
                id="user_admin_123",
                email="admin@example.com",
                password_hash=hash_password("SecurePass123!"),
                name="Admin User"
            ),
            User(
                id="user_john_456",
                email="john@example.com",
                password_hash=hash_password("JohnPass456!"),
                name="John Doe"
            ),
            User(
                id="user_jane_789",
                email="jane@example.com",
                password_hash=hash_password("JanePass789!"),
                name="Jane Smith"
            )
        ]

        for user in users_data:
            session.add(user)

        session.commit()

        # Create sample tasks
        from app.models.task import Task, Priority
        import uuid
        from datetime import datetime, timedelta

        tasks_data = [
            Task(
                id=str(uuid.uuid4()),
                user_id="user_john_456",
                title="Complete project proposal",
                description="Write and review the quarterly project proposal document",
                completed=False,
                priority=Priority.HIGH,
                tags=["work", "important", "deadline"],
                due_date=datetime.utcnow() + timedelta(days=3),
                is_recurring=False
            ),
            Task(
                id=str(uuid.uuid4()),
                user_id="user_john_456",
                title="Buy groceries",
                description="Milk, eggs, bread, fruits",
                completed=True,
                priority=Priority.MEDIUM,
                tags=["personal", "shopping"],
                due_date=datetime.utcnow() - timedelta(days=1),
                is_recurring=False,
                completed_at=datetime.utcnow() - timedelta(days=1)
            ),
            Task(
                id=str(uuid.uuid4()),
                user_id="user_jane_789",
                title="Prepare presentation",
                description="Create slides for the quarterly review",
                completed=False,
                priority=Priority.HIGH,
                tags=["work", "presentation"],
                due_date=datetime.utcnow() + timedelta(days=2),
                is_recurring=False
            ),
            Task(
                id=str(uuid.uuid4()),
                user_id="user_jane_789",
                title="Gym workout",
                description="Cardio and strength training session",
                completed=False,
                priority=Priority.LOW,
                tags=["health", "fitness"],
                due_date=datetime.utcnow() + timedelta(days=1),
                is_recurring=True,
                recurrence_pattern="DAILY"
            )
        ]

        for task in tasks_data:
            session.add(task)

        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
```

### 2. Pytest Fixtures for Database Testing

**Test Database Configuration:**
```python
# tests/conftest.py
import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models.user import User
from app.models.task import Task
from app.utils.security import hash_password
import uuid
from datetime import datetime, timedelta

# Use SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Clean up after test
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    from fastapi.testclient import TestClient
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(session: Session):
    """Create a sample user for testing."""
    from app.models.user import User
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def sample_task(session: Session, sample_user):
    """Create a sample task for testing."""
    from app.models.task import Task, Priority
    task = Task(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        title="Test Task",
        description="This is a test task",
        completed=False,
        priority=Priority.MEDIUM,
        tags=["test", "sample"],
        due_date=datetime.utcnow() + timedelta(days=1),
        is_recurring=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@pytest.fixture
def multiple_users(session: Session):
    """Create multiple users for testing multi-user scenarios."""
    from app.models.user import User
    users = []

    for i in range(3):
        user = User(
            id=str(uuid.uuid4()),
            email=f"user{i}@example.com",
            password_hash=hash_password(f"User{i}Pass123!"),
            name=f"User {i}"
        )
        session.add(user)
        users.append(user)

    session.commit()

    # Create tasks for each user
    from app.models.task import Task, Priority
    for i, user in enumerate(users):
        for j in range(3):  # 3 tasks per user
            task = Task(
                id=str(uuid.uuid4()),
                user_id=user.id,
                title=f"Task {j} for User {i}",
                description=f"Description for task {j} of user {i}",
                completed=j % 2 == 0,  # Alternate completed status
                priority=Priority.HIGH if j == 0 else Priority.MEDIUM,
                tags=[f"user{i}", f"task{j}"],
                due_date=datetime.utcnow() + timedelta(days=j+1),
                is_recurring=j == 2
            )
            session.add(task)

    session.commit()
    return users
```

### 3. CRUD Operation Tests

**Task CRUD Tests:**
```python
# tests/test_tasks.py
import pytest
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.utils.security import hash_password
import uuid
from datetime import datetime, timedelta

def test_create_task(client, session, sample_user):
    """Test creating a new task."""
    task_data = {
        "title": "New Test Task",
        "description": "Description for new task",
        "priority": "HIGH",
        "tags": ["work", "important"],
        "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "is_recurring": False
    }

    response = client.post(f"/api/{sample_user.id}/tasks", json=task_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "New Test Task"
    assert data["description"] == "Description for new task"
    assert data["user_id"] == sample_user.id
    assert data["priority"] == "HIGH"

    # Verify task exists in database
    db_task = session.get(Task, data["id"])
    assert db_task is not None
    assert db_task.title == "New Test Task"

def test_get_task(client, session, sample_task, sample_user):
    """Test retrieving a specific task."""
    response = client.get(f"/api/{sample_user.id}/tasks/{sample_task.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(sample_task.id)
    assert data["title"] == sample_task.title
    assert data["user_id"] == str(sample_user.id)

def test_update_task(client, session, sample_task, sample_user):
    """Test updating a task."""
    update_data = {
        "title": "Updated Task Title",
        "completed": True,
        "priority": "LOW"
    }

    response = client.put(f"/api/{sample_user.id}/tasks/{sample_task.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Task Title"
    assert data["completed"] is True
    assert data["priority"] == "LOW"

    # Verify update in database
    session.refresh(sample_task)
    assert sample_task.title == "Updated Task Title"
    assert sample_task.completed is True

def test_delete_task(client, session, sample_task, sample_user):
    """Test deleting a task."""
    response = client.delete(f"/api/{sample_user.id}/tasks/{sample_task.id}")
    assert response.status_code == 200

    # Verify task no longer exists
    db_task = session.get(Task, sample_task.id)
    assert db_task is None

def test_list_tasks(client, session, multiple_users):
    """Test listing tasks for a specific user."""
    # Get user from the multiple_users fixture
    user = multiple_users[0]

    response = client.get(f"/api/{user.id}/tasks")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # Each user should have 3 tasks created in the fixture
    assert len(data) == 3

    # Verify all tasks belong to the correct user
    for task in data:
        assert task["user_id"] == str(user.id)
```

### 4. Multi-User Isolation Tests

**User Data Isolation Validation:**
```python
# tests/test_security.py
import pytest
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.utils.security import hash_password
import uuid
from datetime import datetime

def test_user_cannot_access_other_users_tasks(client, session, multiple_users):
    """Test that users cannot access tasks belonging to other users."""
    # Get two different users
    user1 = multiple_users[0]
    user2 = multiple_users[1]

    # Get user2's tasks
    user2_tasks = session.exec(
        select(Task).where(Task.user_id == user2.id)
    ).all()

    assert len(user2_tasks) > 0, "User2 should have tasks"

    # Try to access user2's tasks using user1's endpoint
    for task in user2_tasks:
        response = client.get(f"/api/{user1.id}/tasks/{task.id}")
        # Should not be able to access other user's task
        assert response.status_code in [404, 403], f"User1 should not access task {task.id} belonging to user2"

def test_user_can_only_see_own_tasks(client, session, multiple_users):
    """Test that users can only see their own tasks in the list endpoint."""
    user1 = multiple_users[0]
    user2 = multiple_users[1]

    # Get tasks for user1
    response1 = client.get(f"/api/{user1.id}/tasks")
    assert response1.status_code == 200
    user1_tasks = response1.json()

    # Get tasks for user2
    response2 = client.get(f"/api/{user2.id}/tasks")
    assert response2.status_code == 200
    user2_tasks = response2.json()

    # Verify user1 only sees their own tasks
    for task in user1_tasks:
        assert task["user_id"] == str(user1.id)

    # Verify user2 only sees their own tasks
    for task in user2_tasks:
        assert task["user_id"] == str(user2.id)

    # Verify the task lists are different
    user1_task_ids = {task["id"] for task in user1_tasks}
    user2_task_ids = {task["id"] for task in user2_tasks}

    # Sets should be disjoint (no common tasks)
    assert user1_task_ids.isdisjoint(user2_task_ids), "Users should not share tasks"

def test_user_cannot_modify_other_users_tasks(client, session, multiple_users):
    """Test that users cannot modify tasks belonging to other users."""
    user1 = multiple_users[0]
    user2 = multiple_users[1]

    # Get a task belonging to user2
    user2_task = session.exec(
        select(Task)
        .where(Task.user_id == user2.id)
        .limit(1)
    ).first()

    assert user2_task is not None, "User2 should have at least one task"

    # Try to update user2's task using user1's endpoint
    update_data = {"title": "Hacked Task Title"}
    response = client.put(f"/api/{user1.id}/tasks/{user2_task.id}", json=update_data)

    # Should fail with 404 (not found) or 403 (forbidden)
    assert response.status_code in [404, 403], f"User1 should not be able to update task {user2_task.id} belonging to user2"

def test_user_cannot_delete_other_users_tasks(client, session, multiple_users):
    """Test that users cannot delete tasks belonging to other users."""
    user1 = multiple_users[0]
    user2 = multiple_users[1]

    # Get a task belonging to user2
    user2_task = session.exec(
        select(Task)
        .where(Task.user_id == user2.id)
        .limit(1)
    ).first()

    assert user2_task is not None, "User2 should have at least one task"

    # Try to delete user2's task using user1's endpoint
    response = client.delete(f"/api/{user1.id}/tasks/{user2_task.id}")

    # Should fail with 404 (not found) or 403 (forbidden)
    assert response.status_code in [404, 403], f"User1 should not be able to delete task {user2_task.id} belonging to user2"

    # Verify task still exists in database
    db_task = session.get(Task, user2_task.id)
    assert db_task is not None, "Task should still exist after unauthorized delete attempt"
```

### 5. Factory Functions for Test Data

**Test Data Factory:**
```python
# tests/factories.py
import factory
from datetime import datetime, timedelta
import uuid
from app.models.user import User
from app.models.task import Task, Priority
from app.utils.security import hash_password

class UserFactory(factory.Factory):
    """Factory for creating User instances for testing."""
    class Meta:
        model = User

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password_hash = factory.LazyFunction(lambda: hash_password("DefaultPass123!"))
    name = factory.Sequence(lambda n: f"User {n}")
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class TaskFactory(factory.Factory):
    """Factory for creating Task instances for testing."""
    class Meta:
        model = Task

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')
    completed = factory.Faker('boolean')
    priority = factory.Faker('random_element', elements=[p.value for p in Priority])
    tags = factory.LazyFunction(lambda: ["test", "sample"])
    due_date = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(days=1))
    is_recurring = factory.Faker('boolean')
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

# Alternative simple factory functions
def create_user_data(**overrides):
    """Create user data dictionary with overrides."""
    user_data = {
        "id": str(uuid.uuid4()),
        "email": f"user_{uuid.uuid4()}@example.com",
        "password_hash": hash_password("DefaultPass123!"),
        "name": f"Test User {uuid.uuid4()}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    user_data.update(overrides)
    return user_data

def create_task_data(user_id=None, **overrides):
    """Create task data dictionary with overrides."""
    task_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id or str(uuid.uuid4()),
        "title": f"Test Task {uuid.uuid4()}",
        "description": "Sample task description",
        "completed": False,
        "priority": "MEDIUM",
        "tags": ["test", "sample"],
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() if "due_date" not in overrides else overrides["due_date"],
        "is_recurring": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    task_data.update(overrides)
    return task_data
```

### 6. Demo Data Preparation

**Demo Data Script:**
```python
# scripts/create_demo_data.py
import sys
import os
import json
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def create_demo_data():
    """Create demo data for presentations and demonstrations."""

    # Demo users
    demo_users = [
        {
            "id": "demo_user_alice",
            "email": "alice@example.com",
            "name": "Alice Johnson",
            "role": "Project Manager"
        },
        {
            "id": "demo_user_bob",
            "email": "bob@example.com",
            "name": "Bob Smith",
            "role": "Developer"
        },
        {
            "id": "demo_user_charlie",
            "email": "charlie@example.com",
            "name": "Charlie Davis",
            "role": "Designer"
        }
    ]

    # Demo tasks for Alice (Project Manager)
    alice_tasks = [
        {
            "id": "task_alice_1",
            "title": "Review project timeline",
            "description": "Review and update the project timeline with latest estimates",
            "completed": False,
            "priority": "HIGH",
            "tags": ["meeting", "timeline", "review"],
            "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "is_recurring": False
        },
        {
            "id": "task_alice_2",
            "title": "Conduct team standup",
            "description": "Daily standup meeting with the development team",
            "completed": True,
            "priority": "MEDIUM",
            "tags": ["meeting", "standup", "daily"],
            "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "is_recurring": True,
            "recurrence_pattern": "DAILY"
        },
        {
            "id": "task_alice_3",
            "title": "Prepare Q3 report",
            "description": "Compile and format the quarterly progress report",
            "completed": False,
            "priority": "HIGH",
            "tags": ["report", "quarterly", "important"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_recurring": False
        }
    ]

    # Demo tasks for Bob (Developer)
    bob_tasks = [
        {
            "id": "task_bob_1",
            "title": "Implement user authentication",
            "description": "Code the user login and registration functionality",
            "completed": False,
            "priority": "HIGH",
            "tags": ["coding", "authentication", "security"],
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "is_recurring": False
        },
        {
            "id": "task_bob_2",
            "title": "Fix login bug",
            "description": "Resolve the issue with users unable to login after password reset",
            "completed": False,
            "priority": "HIGH",
            "tags": ["bug", "fix", "critical"],
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "is_recurring": False
        },
        {
            "id": "task_bob_3",
            "title": "Code review",
            "description": "Review pull requests from team members",
            "completed": True,
            "priority": "MEDIUM",
            "tags": ["review", "code-quality"],
            "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "is_recurring": True,
            "recurrence_pattern": "WEEKLY"
        }
    ]

    # Demo tasks for Charlie (Designer)
    charlie_tasks = [
        {
            "id": "task_charlie_1",
            "title": "Create wireframes",
            "description": "Design wireframes for the new dashboard interface",
            "completed": False,
            "priority": "HIGH",
            "tags": ["design", "wireframes", "ui"],
            "due_date": (datetime.now() + timedelta(days=4)).isoformat(),
            "is_recurring": False
        },
        {
            "id": "task_charlie_2",
            "title": "Update style guide",
            "description": "Update the design system style guide with new components",
            "completed": False,
            "priority": "MEDIUM",
            "tags": ["design", "style-guide", "documentation"],
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "is_recurring": False
        }
    ]

    demo_data = {
        "users": demo_users,
        "tasks": {
            "demo_user_alice": alice_tasks,
            "demo_user_bob": bob_tasks,
            "demo_user_charlie": charlie_tasks
        },
        "created_at": datetime.now().isoformat()
    }

    # Save to file
    with open("demo_data.json", "w") as f:
        json.dump(demo_data, f, indent=2)

    print("Demo data created successfully!")
    print(f"Created {len(demo_users)} users and {sum(len(tasks) for tasks in demo_data['tasks'].values())} tasks")

    return demo_data

if __name__ == "__main__":
    create_demo_data()
```

### 7. Migration Testing

**Testing Database Migrations with Data:**
```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config
from sqlmodel import create_engine, Session
from app.models.user import User
from app.models.task import Task
from app.utils.security import hash_password
import uuid
from datetime import datetime, timedelta

@pytest.fixture
def alembic_config():
    """Create Alembic configuration for testing."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "sqlite:///./test_migration.db")
    return config

def test_migration_up_down(alembic_config):
    """Test that migrations can be applied and reverted."""
    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Verify tables exist by creating a test record
    engine = create_engine("sqlite:///./test_migration.db")
    with Session(engine) as session:
        user = User(
            id=str(uuid.uuid4()),
            email="migration_test@example.com",
            password_hash=hash_password("TestPass123!"),
            name="Migration Test User"
        )
        session.add(user)
        session.commit()
        user_id = user.id

        # Verify user was created
        retrieved_user = session.get(User, user_id)
        assert retrieved_user is not None
        assert retrieved_user.email == "migration_test@example.com"

    # Downgrade one revision
    command.downgrade(alembic_config, "-1")

    # Upgrade again
    command.upgrade(alembic_config, "head")

def test_migration_data_preservation(alembic_config):
    """Test that data is preserved during migrations."""
    # Create initial data
    engine = create_engine("sqlite:///./test_migration.db")

    with Session(engine) as session:
        # Create a user and task before migration
        user = User(
            id=str(uuid.uuid4()),
            email="data_test@example.com",
            password_hash=hash_password("TestPass123!"),
            name="Data Test User"
        )
        session.add(user)
        session.commit()

        task = Task(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="Test Task Before Migration",
            description="This task should survive migration",
            completed=False,
            created_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()

        task_id = task.id
        session.close()

    # Apply migrations
    command.upgrade(alembic_config, "head")

    # Verify data still exists after migration
    with Session(engine) as session:
        retrieved_task = session.get(Task, task_id)
        assert retrieved_task is not None
        assert retrieved_task.title == "Test Task Before Migration"
        assert retrieved_task.description == "This task should survive migration"
        assert retrieved_task.user_id == user.id
```

### 8. Performance Testing

**Load Testing for Database Operations:**
```python
# tests/test_performance.py
import pytest
import time
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.utils.security import hash_password
import uuid
from datetime import datetime

def test_large_dataset_performance(session, multiple_users):
    """Test performance with a larger dataset."""
    # Add more tasks to create a substantial dataset
    from app.models.task import Task, Priority
    base_time = datetime.utcnow()

    # Create 50 additional tasks for the first user
    for i in range(50):
        task = Task(
            id=str(uuid.uuid4()),
            user_id=multiple_users[0].id,
            title=f"Performance Test Task {i}",
            description=f"Description for performance test task {i}",
            completed=i % 3 == 0,  # Every third task is completed
            priority=Priority.HIGH if i % 10 == 0 else Priority.MEDIUM,
            tags=[f"perf-test-{i % 5}"],
            due_date=base_time + (i * 2) * 24 * 60 * 60,  # Different due dates
            is_recurring=i % 7 == 0  # Some recurring
        )
        session.add(task)

    session.commit()

    # Test query performance
    start_time = time.time()
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == multiple_users[0].id)
        .order_by(Task.created_at)
    ).all()
    query_time = time.time() - start_time

    # Should retrieve 53 tasks (3 original + 50 new)
    assert len(tasks) == 53
    # Query should complete in reasonable time (under 100ms for this dataset)
    assert query_time < 0.1, f"Query took too long: {query_time:.3f}s"

def test_concurrent_user_performance(session, multiple_users):
    """Test performance with multiple users accessing data concurrently."""
    import threading
    import time

    results = {}

    def query_user_tasks(user_idx):
        start_time = time.time()
        user_tasks = session.exec(
            select(Task)
            .where(Task.user_id == multiple_users[user_idx].id)
        ).all()
        results[user_idx] = {
            'count': len(user_tasks),
            'time': time.time() - start_time
        }

    # Create threads for each user
    threads = []
    for i in range(len(multiple_users)):
        thread = threading.Thread(target=query_user_tasks, args=(i,))
        threads.append(thread)

    # Start all threads
    start_time = time.time()
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time

    # Verify all queries completed successfully
    for user_idx in range(len(multiple_users)):
        assert user_idx in results
        assert results[user_idx]['count'] == 3  # Each user has 3 tasks
        assert results[user_idx]['time'] > 0

    # Total time should be reasonable for concurrent execution
    assert total_time < 1.0, f"Concurrent queries took too long: {total_time:.3f}s"
```

### 9. Test Data Quality Assurance

**Data Validation Tests:**
```python
# tests/test_data_validation.py
import pytest
from app.models.user import User
from app.models.task import Task, Priority
from app.utils.security import hash_password
import uuid
from datetime import datetime, timedelta

def test_user_data_validation(session):
    """Test that user data meets validation requirements."""
    # Test valid user creation
    valid_user = User(
        id=str(uuid.uuid4()),
        email="valid@example.com",
        password_hash=hash_password("ValidPass123!"),
        name="Valid User"
    )

    # Test that required fields are present
    assert valid_user.email is not None
    assert valid_user.name is not None
    assert valid_user.password_hash is not None
    assert len(valid_user.name) > 0

    # Test email format validation (would be handled by Pydantic in real implementation)
    assert "@" in valid_user.email
    assert "." in valid_user.email

def test_task_data_validation(session, sample_user):
    """Test that task data meets validation requirements."""
    from datetime import timezone

    # Test valid task creation
    valid_task = Task(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        title="Valid Task Title",
        description="Valid task description",
        completed=False,
        priority=Priority.MEDIUM,
        tags=["tag1", "tag2"],
        due_date=datetime.now() + timedelta(days=1),
        is_recurring=False
    )

    # Test required fields
    assert valid_task.title is not None
    assert len(valid_task.title) > 0
    assert len(valid_task.title) <= 200  # Assuming max length constraint
    assert valid_task.user_id == sample_user.id
    assert valid_task.priority in [p.value for p in Priority]

    # Test priority enum validation
    assert valid_task.priority in [p.value for p in Priority]

def test_task_constraints(session, sample_user):
    """Test task-specific constraints."""
    # Test that completed tasks have valid completion dates
    completed_task = Task(
        id=str(uuid.uuid4()),
        user_id=sample_user.id,
        title="Completed Task",
        completed=True,
        completed_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    # If task is completed, it should have a completed_at date
    if completed_task.completed:
        assert completed_task.completed_at is not None
        # completed_at should not be before created_at
        assert completed_task.completed_at >= completed_task.created_at
```

### 10. Data Seeding and Testing Checklist

- [ ] Create sample users with realistic data
- [ ] Generate tasks with various priorities, statuses, and due dates
- [ ] Include recurring tasks in test data
- [ ] Create test data for edge cases (empty tags, null descriptions, etc.)
- [ ] Set up pytest fixtures for consistent test data
- [ ] Validate multi-user isolation in tests
- [ ] Test CRUD operations for all entity types
- [ ] Include performance tests with larger datasets
- [ ] Verify data validation constraints
- [ ] Test migration scenarios with existing data

## References

- **Database Spec**: `@specs/database/schema.md` for schema definitions
- **Testing Spec**: `@specs/testing/backend-testing.md` for testing requirements
- **Authentication Spec**: `@specs/features/authentication.md` for user validation
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com for ORM patterns
- **Pytest Documentation**: https://docs.pytest.org for testing framework