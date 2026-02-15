# Data Model: Multi-User Full-Stack Todo Web Application

## Entity Definitions

### User Entity
```
User:
- id: UUID (primary key)
- email: str (unique, indexed)
- hashed_password: str (encrypted)
- created_at: datetime (indexed)
- updated_at: datetime
```

**Relationships**:
- One-to-Many: User → Task (via user_id foreign key)
- One-to-Many: User → Tag (via user_id foreign key)

**Validation Rules**:
- email: Valid email format, unique across all users
- hashed_password: bcrypt or argon2 hashed, never stored in plaintext

### Task Entity
```
Task:
- id: UUID (primary key)
- title: str (indexed, max 255 chars)
- description: str (optional, max 1000 chars)
- status: str (enum: 'todo', 'completed', default: 'todo', indexed)
- priority: str (enum: 'low', 'medium', 'high', 'none', default: 'none', indexed)
- due_date: datetime (optional, indexed)
- recurrence_pattern: str (enum: 'none', 'daily', 'weekly', 'monthly', 'yearly', default: 'none')
- user_id: UUID (foreign key to User, indexed)
- created_at: datetime (indexed)
- updated_at: datetime
```

**Relationships**:
- Many-to-One: Task → User (via user_id foreign key)
- Many-to-Many: Task ↔ Tag (via TaskTag junction table)

**Validation Rules**:
- title: Required, 1-255 characters
- due_date: If provided, must be in the future
- recurrence_pattern: Only valid enum values
- user_id: Must reference an existing user

**State Transitions**:
- Status: 'todo' ↔ 'completed' (via toggle completion endpoint)

### Tag Entity
```
Tag:
- id: UUID (primary key)
- name: str (indexed, max 20 chars)
- user_id: UUID (foreign key to User, indexed)
- created_at: datetime
```

**Relationships**:
- Many-to-One: Tag → User (via user_id foreign key)
- Many-to-Many: Tag ↔ Task (via TaskTag junction table)

**Validation Rules**:
- name: Required, 1-20 characters, alphanumeric with spaces/hyphens
- user_id: Must reference an existing user
- Unique constraint: (user_id, name) - users can't have duplicate tag names

### TaskTag Relationship (Many-to-Many)
```
TaskTag:
- task_id: UUID (foreign key to Task, indexed)
- tag_id: UUID (foreign key to Tag, indexed)
- primary key: (task_id, tag_id)
```

**Relationships**:
- Many-to-One: TaskTag → Task
- Many-to-One: TaskTag → Tag

**Validation Rules**:
- task_id: Must reference an existing task
- tag_id: Must reference an existing tag for the same user
- Both foreign keys must belong to the same user (enforced by application logic)

## Database Constraints

### Primary Keys
- All entities use UUID primary keys for consistency and security

### Foreign Keys
- All foreign keys have appropriate constraints
- Cascading delete: Deleting a user deletes all their tasks and tags
- Referential integrity enforced at database level

### Indexes
- User.email: Unique index for fast login
- Task.user_id: Index for user isolation queries
- Task.status: Index for filtering
- Task.priority: Index for sorting
- Task.due_date: Index for due date queries
- Tag.user_id: Index for user isolation queries

### Security Constraints
- User isolation enforced at database level: All queries must include user_id
- No cross-user access possible at database level without application logic bypass

## API Validation Rules

### Input Validation
- All string inputs are sanitized against XSS
- Date/time inputs validated against format and range
- Priority values restricted to enum values
- Email format validated using standard regex

### Business Logic Validation
- Users can only modify their own tasks and tags
- Due dates must be in the future
- Recurring tasks follow calendar patterns
- Task titles must be unique per user (optional business rule)

## State Transition Diagrams

### Task Status Transitions
```
[ANY STATUS] → toggle completion → [OPPOSITE STATUS]
Example: 'todo' → PATCH /complete → 'completed'
Example: 'completed' → PATCH /complete → 'todo'
```

### User Authentication States
```
[UNAUTHENTICATED] → login/signup → [AUTHENTICATED with JWT]
[AUTHENTICATED] → token expiry → [UNAUTHENTICATED]
[AUTHENTICATED] → logout → [UNAUTHENTICATED]
```