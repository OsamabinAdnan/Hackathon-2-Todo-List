# Feature: Task CRUD Operations

**Feature ID**: `task-crud`
**Status**: In Progress
**Priority**: Critical
**Dependencies**: Authentication (users must be logged in)

---

## Overview

Comprehensive task management system with three progressive levels:
- **Level 1 (Basic)**: Core CRUD operations
- **Level 2 (Intermediate)**: Organization features (priorities, tags, filtering, sorting)
- **Level 3 (Advanced)**: Intelligence features (recurring tasks, reminders, notifications)

---

## User Stories

### Level 1: Basic CRUD

#### US-1.1: Create Task
**As a** logged-in user
**I want to** create a new task
**So that** I can track things I need to do

**Acceptance Criteria:**
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task is automatically associated with logged-in user
- Task is created with status "incomplete" by default
- Created timestamp is automatically set
- Returns task ID upon successful creation

**Validation Rules:**
- Title cannot be empty or whitespace-only
- Title max length: 200 characters
- Description max length: 1000 characters
- User must be authenticated (JWT token required)

---

#### US-1.2: View All Tasks
**As a** logged-in user
**I want to** view all my tasks
**So that** I can see what I need to work on

**Acceptance Criteria:**
- Only show tasks belonging to the logged-in user
- Display task ID, title, status (complete/incomplete), created date
- Tasks are displayed in reverse chronological order (newest first) by default
- Empty state shown when user has no tasks
- Shows task count at the top

**Display Fields:**
- Task ID
- Title (truncated if longer than 50 chars)
- Status indicator (✓ complete / ○ incomplete)
- Created date (formatted: "Jan 2, 2026")
- Priority badge (if set)
- Tags (if any)

---

#### US-1.3: Update Task
**As a** logged-in user
**I want to** update a task's details
**So that** I can correct or enhance task information

**Acceptance Criteria:**
- User can update title and/or description
- User can only update their own tasks
- Updated timestamp is automatically set
- Original created date remains unchanged
- Returns updated task object

**Validation Rules:**
- Same validation as create (title 1-200 chars, description max 1000)
- Task must exist and belong to authenticated user
- At least one field (title or description) must be provided

---

#### US-1.4: Delete Task
**As a** logged-in user
**I want to** delete a task
**So that** I can remove tasks I no longer need

**Acceptance Criteria:**
- User can only delete their own tasks
- Confirmation required before deletion (frontend modal)
- Task is permanently deleted from database
- Returns success confirmation
- No "soft delete" - hard delete only

**Security:**
- Verify task ownership before deletion
- Return 404 if task doesn't exist
- Return 401 if task belongs to different user

---

#### US-1.5: Mark Task Complete/Incomplete
**As a** logged-in user
**I want to** toggle a task's completion status
**So that** I can track what I've accomplished

**Acceptance Criteria:**
- User can toggle status from incomplete → complete
- User can toggle status from complete → incomplete
- Completed timestamp is set when marking complete
- Completed timestamp is cleared when marking incomplete
- User can only toggle their own tasks

**Special Behavior:**
- If task is recurring (Level 3), completing triggers auto-reschedule
- Completed tasks remain visible in task list (filterable in Level 2)

---

## Level 2: Intermediate Features

### US-2.1: Priority Levels
**As a** logged-in user
**I want to** assign priority levels to tasks
**So that** I can focus on what's most important

**Acceptance Criteria:**
- Four priority levels: HIGH, MEDIUM, LOW, NONE
- Priority can be set during task creation
- Priority can be updated at any time
- Default priority is NONE if not specified
- Priority displayed with color coding:
  - HIGH: Red (#EF4444)
  - MEDIUM: Yellow (#F59E0B)
  - LOW: Green (#10B981)
  - NONE: Gray (#6B7280)

**API Field:**
- `priority: "HIGH" | "MEDIUM" | "LOW" | "NONE"`

---

### US-2.2: Tags/Categories
**As a** logged-in user
**I want to** add tags to tasks
**So that** I can categorize and organize them

**Acceptance Criteria:**
- Tasks can have multiple tags (comma-separated input)
- Each tag max 20 characters
- Tags are case-insensitive (stored lowercase)
- Tags displayed as badges/chips
- User can add/remove tags when creating or updating
- Duplicate tags automatically removed

**Validation:**
- Max 10 tags per task
- Each tag: 1-20 characters
- Allowed characters: alphanumeric, hyphens, underscores
- Tags trimmed of leading/trailing whitespace

**Examples:**
- Input: "work, personal, urgent"
- Stored: ["work", "personal", "urgent"]

---

### US-2.3: Search Tasks
**As a** logged-in user
**I want to** search for tasks by keyword
**So that** I can quickly find specific tasks

**Acceptance Criteria:**
- Search across title, description, and tags
- Case-insensitive search
- Partial match supported (e.g., "meet" matches "meeting")
- Highlight matching terms in results (frontend)
- Search returns tasks in relevance order
- Empty results show "No tasks found" message

**Search Behavior:**
- If keyword found in title → highest relevance
- If keyword found in description → medium relevance
- If keyword found in tags → lower relevance
- Multiple keyword matches → higher score

---

### US-2.4: Filter Tasks
**As a** logged-in user
**I want to** filter tasks by various criteria
**So that** I can view specific subsets of tasks

**Acceptance Criteria:**
- Filter by status: "all" | "todo" | "completed"
- Filter by priority: "all" | "HIGH" | "MEDIUM" | "LOW" | "NONE"
- Filter by tags: Select one or more tags (ANY-match logic)
- Multiple filters can be combined (AND logic between filter types)
- Filter state persists during session (frontend state)

**Filter Combinations:**
- Status=todo AND Priority=HIGH → Show incomplete high-priority tasks
- Tags=["work", "urgent"] → Show tasks with "work" OR "urgent" tag
- Status=completed AND Tags=["personal"] → Show completed personal tasks

**UI Components:**
- Status: Segmented control or tabs
- Priority: Dropdown or filter chips
- Tags: Multi-select dropdown or tag cloud

---

### US-2.5: Sort Tasks
**As a** logged-in user
**I want to** sort tasks by different criteria
**So that** I can view them in my preferred order

**Acceptance Criteria:**
- Sort by Priority (HIGH → MEDIUM → LOW → NONE)
- Sort by Created Date (newest first or oldest first)
- Sort by Title (A-Z or Z-A)
- Sort by Due Date (Level 3 feature, earliest first)
- Default sort: Created Date (newest first)
- Sort direction toggleable (ascending/descending)

**Secondary Sorting:**
- Priority → then by Due Date → then by Title
- Due Date → then by Priority → then by Title
- Title → then by Priority

**UI Component:**
- Dropdown with sort options
- Icon indicating sort direction (↑ ascending, ↓ descending)

---

## Level 3: Advanced Features

### US-3.1: Recurring Tasks
**As a** logged-in user
**I want to** set tasks as recurring
**So that** repeating tasks automatically reschedule

**Acceptance Criteria:**
- Three recurrence patterns: DAILY, WEEKLY, MONTHLY
- Recurring tasks must have a due date
- When marked complete, new instance auto-created with next due date
- When due date passes (without completion), auto-reschedule
- Original task marked complete, new task created with next due date
- Recurring indicator shown in UI (🔁 icon)

**Recurrence Logic:**
- DAILY: Due date + 1 day
- WEEKLY: Due date + 7 days
- MONTHLY: Due date + 1 month (handle edge cases)

**Edge Cases:**
- Jan 31 + 1 month → Feb 28 (or Feb 29 in leap year)
- Oct 31 + 1 month → Nov 30
- Feb 29 (leap year) → Mar 29 in non-leap year

**API Fields:**
- `is_recurring: boolean`
- `recurrence_pattern: "DAILY" | "WEEKLY" | "MONTHLY" | null`

---

### US-3.2: Due Dates & Times
**As a** logged-in user
**I want to** set due dates with specific times
**So that** I can schedule tasks precisely

**Acceptance Criteria:**
- Due date format: YYYY-MM-DD HH:MM (24-hour)
- Date-only format: YYYY-MM-DD (defaults to 00:00)
- Future dates only (validation: must be >= current datetime)
- Due date is optional
- Due date can be updated at any time
- Overdue tasks highlighted in red (past due datetime)
- Due soon tasks highlighted in yellow (within 60 minutes)

**Display Formats:**
- With time: "Jan 15, 2026 at 2:30 PM"
- Without time (00:00): "Jan 15, 2026" (no time shown)
- Relative: "Due in 2 hours" (frontend humanization)

**Validation:**
- Due date cannot be in the past
- If recurring task, due date is required
- Time component is optional (defaults to 00:00)

---

### US-3.3: Smart Reminders
**As a** logged-in user
**I want to** receive notifications for due tasks
**So that** I don't miss important deadlines

**Acceptance Criteria:**
- Browser notifications for overdue tasks (past due datetime)
- Browser notifications for tasks due within 60 minutes
- Notification shows task title and due time
- Notification triggers when:
  - User logs in (check all due/overdue tasks)
  - User views dashboard (check in background)
  - Every 5 minutes while app is open (background polling)
- User can dismiss notifications
- Tasks with time=00:00 excluded from reminders (date-only deadlines)

**Notification Content:**
- Title: "Task Reminder"
- Body: "[Task Title] is due in 30 minutes" or "[Task Title] is overdue by 2 hours"
- Icon: App logo or ⏰ emoji
- Action: Click to navigate to task detail

**Browser API:**
- Request notification permission on first login
- Use Web Notifications API
- Fallback to in-app toasts if permission denied

**Reminder Panel (UI):**
- Show at top of dashboard
- Overdue section (red): List of overdue tasks
- Due soon section (yellow): List of tasks due within 60 minutes
- Humanized time: "2 hours overdue", "due in 30 min"

---

## Data Model

### Task Entity

```typescript
interface Task {
  id: string;                          // UUID
  user_id: string;                     // Foreign key to users table
  title: string;                       // Required, 1-200 chars
  description: string | null;          // Optional, max 1000 chars
  completed: boolean;                  // Default: false
  priority: "HIGH" | "MEDIUM" | "LOW" | "NONE";  // Default: NONE
  tags: string[];                      // Array of strings, max 10 tags
  due_date: string | null;             // ISO 8601: "2026-01-15T14:30:00Z"
  is_recurring: boolean;               // Default: false
  recurrence_pattern: "DAILY" | "WEEKLY" | "MONTHLY" | null;
  created_at: string;                  // Auto-generated timestamp
  updated_at: string;                  // Auto-updated timestamp
  completed_at: string | null;         // Timestamp when marked complete
}
```

---

## API Endpoints

See `@specs/api/rest-endpoints.md` for full API documentation.

**Summary:**
- `GET /api/{user_id}/tasks` - List tasks (with filters, sort, search)
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task details
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

---

## UI/UX Requirements

### Dashboard Layout
- **Sidebar**: Navigation, filters, tags list
- **Main Content**: Task list with cards
- **Header**: Search bar, sort dropdown, "New Task" button
- **Empty State**: Friendly illustration + "Create your first task" CTA

### Task Card Design
- Glassmorphism effect (backdrop-blur)
- Checkbox for completion toggle (left)
- Title (prominent, bold)
- Description preview (2 lines max, ellipsis)
- Priority badge (top-right corner)
- Tags (below description, chips)
- Due date (bottom-left, with icon)
- Recurring indicator (🔁 icon if recurring)
- Actions menu (three-dot menu: Edit, Delete)

### Animations
- Task card hover: Subtle lift effect (translate-y: -2px)
- Checkbox toggle: Smooth checkmark animation (GSAP)
- Task creation: Slide in from top (Framer Motion)
- Task deletion: Fade out + slide left
- Completion: Strikethrough animation + confetti (optional)

### Interactions
- Click card → Expand to show full details (modal or side panel)
- Drag to reorder (optional, low priority)
- Keyboard shortcuts:
  - `N` - New task
  - `F` - Focus search
  - `↑/↓` - Navigate tasks
  - `Space` - Toggle completion

---

## Error Handling

### Frontend Errors
- Network failure: Show toast "Failed to load tasks. Retrying..."
- Validation error: Inline error messages below inputs
- 401 Unauthorized: Redirect to login page
- 404 Task not found: Show "Task no longer exists" message

### Backend Errors
- 400 Bad Request: Invalid input (return validation errors)
- 401 Unauthorized: Invalid/expired JWT token
- 403 Forbidden: User doesn't own this task
- 404 Not Found: Task doesn't exist
- 500 Internal Server Error: Generic error message (log details server-side)

---

## Testing Requirements

### Unit Tests
- Task creation with valid/invalid data
- Task update with partial data
- Task deletion with ownership verification
- Priority assignment and validation
- Tag parsing and normalization
- Recurring task rescheduling logic
- Due date validation (future dates only)

### Integration Tests
- Create task → Verify in database
- Update task → Verify changes persisted
- Delete task → Verify removed from database
- Filter tasks by status → Verify correct subset returned
- Search tasks by keyword → Verify matching results
- Toggle completion of recurring task → Verify new task created

### E2E Tests
- User creates task → Task appears in list
- User completes task → Checkbox checked, status updated
- User deletes task → Task removed from list
- User filters by priority → Only high-priority tasks shown
- User searches "meeting" → Tasks with "meeting" in title/description shown

---

## Performance Considerations

- **Lazy Loading**: Load tasks in batches (20 per page)
- **Debounce Search**: 300ms delay before triggering search API call
- **Optimistic Updates**: Update UI immediately, sync with backend asynchronously
- **Caching**: Cache task list in frontend state, invalidate on mutations
- **Indexing**: Database indexes on `user_id`, `completed`, `due_date`, `priority`

---

## Accessibility

- **WCAG 2.1 AA Compliance**
- Keyboard navigation for all interactions
- Screen reader labels for icons and buttons
- Focus indicators (ring-2 ring-blue-500)
- Color contrast ratios: 4.5:1 minimum
- ARIA labels for dynamic content (task count, filter status)

---

## Success Metrics

- User can create task in < 3 seconds
- Task list loads in < 500ms
- Search returns results in < 200ms
- 60fps animations on all interactions
- Zero unauthorized access to other users' tasks (security tests pass)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
