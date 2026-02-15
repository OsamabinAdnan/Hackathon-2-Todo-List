# End-to-End (E2E) Testing Specification

**Test Framework**: Playwright
**Coverage**: Critical user flows (100%)
**Browsers**: Chrome, Firefox, Safari
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## E2E Testing Philosophy

E2E tests validate **complete user flows** from browser to database:
- Simulate real user behavior
- Test actual browser rendering
- Verify frontend-backend integration
- Ensure cross-browser compatibility

**Goal**: Confidence that real users can complete critical tasks.

---

## Critical User Flows

### Priority 1: Essential Flows (Must Pass)
1. **User Signup → Login → Dashboard**
2. **Create Task → View Task → Complete Task**
3. **Login → Filter Tasks → Logout**
4. **Create Recurring Task → Complete → Verify Auto-Reschedule**

### Priority 2: Important Flows
5. **Search Tasks → View Results**
6. **Sort Tasks by Priority**
7. **Edit Task Details**
8. **Delete Task with Confirmation**

### Priority 3: Advanced Flows
9. **Set Due Date → Verify Reminder**
10. **Create Task with Tags → Filter by Tag**

---

## E2E Test Structure

```
frontend/e2e/
├── auth.spec.ts                   # Authentication flows (300+ lines)
├── tasks-crud.spec.ts             # Task CRUD operations (400+ lines)
├── tasks-filters.spec.ts          # Filtering and sorting (250+ lines)
├── tasks-recurring.spec.ts        # Recurring tasks (200+ lines)
├── tasks-reminders.spec.ts        # Due dates and reminders (150+ lines)
├── accessibility.spec.ts          # A11y tests (200+ lines)
├── fixtures/                      # Test data and helpers
│   ├── auth.ts
│   └── tasks.ts
└── playwright.config.ts
```

---

## Test Cases

### E2E-AUTH-001: Complete Signup Flow
```typescript
import { test, expect } from '@playwright/test';

test('user can sign up, create task, and logout', async ({ page }) => {
  // Navigate to signup
  await page.goto('/signup');

  // Fill signup form
  await page.getByLabel('Email').fill('newuser@example.com');
  await page.getByLabel('Password', { exact: true }).fill('SecurePass123!');
  await page.getByLabel('Confirm Password').fill('SecurePass123!');
  await page.getByLabel('Name').fill('New User');

  // Submit form
  await page.getByRole('button', { name: /create account/i }).click();

  // Should redirect to dashboard
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/welcome/i)).toBeVisible();

  // Verify user name displayed
  await expect(page.getByText('New User')).toBeVisible();

  // Create a task
  await page.getByRole('button', { name: /new task/i }).click();
  await page.getByLabel('Title').fill('My First Task');
  await page.getByLabel('Description').fill('This is my first task');
  await page.getByRole('button', { name: /create/i }).click();

  // Verify task appears in list
  await expect(page.getByText('My First Task')).toBeVisible();

  // Logout
  await page.getByRole('button', { name: /user menu/i }).click();
  await page.getByRole('menuitem', { name: /log out/i }).click();

  // Should redirect to login
  await expect(page).toHaveURL(/\/login/);
});
```

### E2E-AUTH-002: Login with Existing Account
```typescript
test('user can login with existing credentials', async ({ page }) => {
  // Navigate to login
  await page.goto('/login');

  // Fill login form
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('TestPass123!');

  // Submit
  await page.getByRole('button', { name: /log in/i }).click();

  // Should redirect to dashboard
  await expect(page).toHaveURL(/\/dashboard/);

  // Verify previously created tasks are visible
  await expect(page.getByText(/my tasks/i)).toBeVisible();
});
```

### E2E-AUTH-003: Invalid Credentials Rejected
```typescript
test('login with wrong password shows error', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('WrongPassword123!');
  await page.getByRole('button', { name: /log in/i }).click();

  // Should show error message
  await expect(page.getByText(/invalid email or password/i)).toBeVisible();

  // Should not redirect
  await expect(page).toHaveURL(/\/login/);
});
```

### E2E-TASK-001: Create Task
```typescript
test('user can create task with all fields', async ({ page }) => {
  // Login first (using fixture)
  await loginAsTestUser(page);

  // Navigate to dashboard
  await page.goto('/dashboard');

  // Click new task button
  await page.getByRole('button', { name: /new task/i }).click();

  // Fill form
  await page.getByLabel('Title').fill('Complete E2E Testing');
  await page.getByLabel('Description').fill('Write comprehensive E2E tests for all flows');
  await page.getByLabel('Priority').selectOption('HIGH');
  await page.getByLabel('Tags').fill('work, testing');
  await page.getByLabel('Due Date').fill('2026-01-15');
  await page.getByLabel('Due Time').fill('14:30');

  // Submit
  await page.getByRole('button', { name: /create task/i }).click();

  // Verify task appears
  await expect(page.getByText('Complete E2E Testing')).toBeVisible();
  await expect(page.getByText('HIGH')).toBeVisible();
  await expect(page.getByText('work')).toBeVisible();
  await expect(page.getByText('Jan 15, 2026')).toBeVisible();
});
```

### E2E-TASK-002: Mark Task Complete
```typescript
test('user can mark task as complete', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Find task checkbox
  const taskCard = page.getByText('Test Task').locator('..');
  const checkbox = taskCard.getByRole('checkbox');

  // Mark complete
  await checkbox.check();

  // Verify visual feedback
  await expect(taskCard.getByText('Test Task')).toHaveClass(/line-through/);

  // Reload page to verify persistence
  await page.reload();
  await expect(checkbox).toBeChecked();
});
```

### E2E-TASK-003: Filter Tasks by Status
```typescript
test('user can filter tasks by completion status', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Click "Completed" filter
  await page.getByRole('tab', { name: /completed/i }).click();

  // Only completed tasks should be visible
  const taskCards = page.locator('[data-testid="task-card"]');
  const count = await taskCards.count();

  for (let i = 0; i < count; i++) {
    const checkbox = taskCards.nth(i).getByRole('checkbox');
    await expect(checkbox).toBeChecked();
  }
});
```

### E2E-TASK-004: Search Tasks
```typescript
test('user can search tasks by keyword', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Type in search box
  await page.getByPlaceholder(/search tasks/i).fill('meeting');

  // Wait for debounce
  await page.waitForTimeout(500);

  // Only tasks with "meeting" should be visible
  const taskCards = page.locator('[data-testid="task-card"]');
  const count = await taskCards.count();

  for (let i = 0; i < count; i++) {
    const text = await taskCards.nth(i).textContent();
    expect(text?.toLowerCase()).toContain('meeting');
  }
});
```

### E2E-TASK-005: Edit Task
```typescript
test('user can edit task details', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Open task menu
  const taskCard = page.getByText('Test Task').locator('..');
  await taskCard.getByRole('button', { name: /menu/i }).click();

  // Click edit
  await page.getByRole('menuitem', { name: /edit/i }).click();

  // Update fields
  await page.getByLabel('Title').fill('Updated Task Title');
  await page.getByLabel('Priority').selectOption('MEDIUM');

  // Save
  await page.getByRole('button', { name: /save/i }).click();

  // Verify updates
  await expect(page.getByText('Updated Task Title')).toBeVisible();
  await expect(page.getByText('MEDIUM')).toBeVisible();
});
```

### E2E-TASK-006: Delete Task
```typescript
test('user can delete task with confirmation', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  const originalTaskTitle = 'Task to Delete';

  // Create task to delete
  await page.getByRole('button', { name: /new task/i }).click();
  await page.getByLabel('Title').fill(originalTaskTitle);
  await page.getByRole('button', { name: /create/i }).click();

  // Wait for task to appear
  await expect(page.getByText(originalTaskTitle)).toBeVisible();

  // Open menu and click delete
  const taskCard = page.getByText(originalTaskTitle).locator('..');
  await taskCard.getByRole('button', { name: /menu/i }).click();
  await page.getByRole('menuitem', { name: /delete/i }).click();

  // Confirm deletion
  await page.getByRole('button', { name: /confirm/i }).click();

  // Task should disappear
  await expect(page.getByText(originalTaskTitle)).not.toBeVisible();

  // Reload to verify
  await page.reload();
  await expect(page.getByText(originalTaskTitle)).not.toBeVisible();
});
```

### E2E-RECURRING-001: Weekly Recurring Task
```typescript
test('completing weekly task creates next occurrence', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Create recurring task
  await page.getByRole('button', { name: /new task/i }).click();
  await page.getByLabel('Title').fill('Weekly Team Meeting');
  await page.getByLabel('Due Date').fill('2026-01-06');
  await page.getByLabel('Due Time').fill('09:00');
  await page.getByLabel('Recurring').check();
  await page.getByLabel('Recurrence Pattern').selectOption('WEEKLY');
  await page.getByRole('button', { name: /create/i }).click();

  // Complete the task
  const taskCard = page.getByText('Weekly Team Meeting').locator('..');
  await taskCard.getByRole('checkbox').check();

  // Should show notification about new task created
  await expect(page.getByText(/next occurrence created/i)).toBeVisible();

  // Verify new task with +7 days due date
  await expect(page.getByText('Weekly Team Meeting')).toBeVisible();
  await expect(page.getByText('Jan 13, 2026')).toBeVisible();
});
```

### E2E-A11Y-001: Keyboard Navigation
```typescript
test('dashboard is fully keyboard navigable', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Tab through interface
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: /new task/i })).toBeFocused();

  await page.keyboard.press('Tab');
  // Should move to first task card

  // Press Enter to open task
  await page.keyboard.press('Enter');

  // Escape to close
  await page.keyboard.press('Escape');
});
```

### E2E-A11Y-002: Screen Reader Compatibility
```typescript
test('important elements have proper ARIA labels', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Check for ARIA landmarks
  await expect(page.getByRole('navigation')).toBeVisible();
  await expect(page.getByRole('main')).toBeVisible();

  // Check task count is announced
  const taskCount = page.getByRole('status', { name: /tasks/i });
  await expect(taskCount).toBeVisible();
});
```

---

## Test Fixtures

### fixtures/auth.ts
```typescript
import { Page } from '@playwright/test';

export async function loginAsTestUser(page: Page) {
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('TestPass123!');
  await page.getByRole('button', { name: /log in/i }).click();
  await page.waitForURL(/\/dashboard/);
}

export async function createTestUser(page: Page, email: string, password: string, name: string) {
  await page.goto('/signup');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByLabel('Confirm Password').fill(password);
  await page.getByLabel('Name').fill(name);
  await page.getByRole('button', { name: /create account/i }).click();
  await page.waitForURL(/\/dashboard/);
}
```

### fixtures/tasks.ts
```typescript
import { Page } from '@playwright/test';

export async function createTask(
  page: Page,
  title: string,
  options?: {
    description?: string;
    priority?: 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
    tags?: string;
    dueDate?: string;
  }
) {
  await page.getByRole('button', { name: /new task/i }).click();
  await page.getByLabel('Title').fill(title);

  if (options?.description) {
    await page.getByLabel('Description').fill(options.description);
  }

  if (options?.priority) {
    await page.getByLabel('Priority').selectOption(options.priority);
  }

  if (options?.tags) {
    await page.getByLabel('Tags').fill(options.tags);
  }

  if (options?.dueDate) {
    await page.getByLabel('Due Date').fill(options.dueDate);
  }

  await page.getByRole('button', { name: /create/i }).click();
  await page.waitForSelector(`text=${title}`);
}
```

---

## Running E2E Tests

### Development
```bash
# Run all tests
npx playwright test

# Run specific file
npx playwright test auth.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### CI/CD
```bash
# Run all browsers in parallel
npx playwright test --workers=3

# Generate HTML report
npx playwright show-report

# Run with retries
npx playwright test --retries=2
```

---

## Visual Regression Testing (Optional)

```typescript
test('dashboard matches screenshot', async ({ page }) => {
  await loginAsTestUser(page);
  await page.goto('/dashboard');

  // Take screenshot
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
  });
});
```

---

## Performance Testing

```typescript
import { test, expect } from '@playwright/test';

test('dashboard loads within 2 seconds', async ({ page }) => {
  await loginAsTestUser(page);

  const start = Date.now();
  await page.goto('/dashboard');
  await page.waitForSelector('[data-testid="task-list"]');
  const duration = Date.now() - start;

  expect(duration).toBeLessThan(2000);
});
```

---

## Success Criteria

E2E testing is complete when:

- ✅ All Priority 1 flows passing (100%)
- ✅ All Priority 2 flows passing (90%)
- ✅ Tests pass in Chrome, Firefox, and Safari
- ✅ Accessibility tests passing (keyboard, screen reader)
- ✅ Performance benchmarks met (< 2s page load)
- ✅ Zero flaky tests (tests are reliable)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
