# Frontend Testing Specification

**Test Framework**: Vitest + React Testing Library
**E2E Framework**: Playwright
**Coverage Target**: 70%+ overall, 90%+ for critical components
**Methodology**: Test-Driven Development (TDD)
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Testing Stack

### Unit & Component Testing
- **Vitest**: Fast unit test framework (Vite-native)
- **React Testing Library**: Component testing library
- **@testing-library/jest-dom**: Custom matchers
- **@testing-library/user-event**: Simulate user interactions
- **MSW (Mock Service Worker)**: API mocking
- **@vitest/coverage-c8**: Code coverage

### E2E Testing
- **Playwright**: Cross-browser E2E testing
- **playwright/test**: Test runner

---

## Test Structure

```
frontend/
├── __tests__/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.test.tsx
│   │   │   ├── Card.test.tsx
│   │   │   └── Input.test.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.test.tsx            (200+ lines)
│   │   │   └── SignupForm.test.tsx           (250+ lines)
│   │   ├── tasks/
│   │   │   ├── TaskCard.test.tsx             (300+ lines)
│   │   │   ├── TaskForm.test.tsx             (250+ lines)
│   │   │   ├── TaskList.test.tsx             (200+ lines)
│   │   │   ├── TaskFilters.test.tsx          (150+ lines)
│   │   │   └── TaskSearch.test.tsx           (100+ lines)
│   │   └── dashboard/
│   │       ├── Dashboard.test.tsx            (250+ lines)
│   │       └── Sidebar.test.tsx              (150+ lines)
│   ├── lib/
│   │   ├── api.test.ts                       (300+ lines)
│   │   ├── auth.test.ts                      (200+ lines)
│   │   ├── utils.test.ts                     (150+ lines)
│   │   └── validation.test.ts                (150+ lines)
│   ├── hooks/
│   │   ├── useTasks.test.ts                  (200+ lines)
│   │   └── useAuth.test.ts                   (150+ lines)
│   └── setup.ts                              # Test setup & mocks
├── e2e/
│   ├── auth.spec.ts                          (300+ lines)
│   ├── tasks-crud.spec.ts                    (400+ lines)
│   ├── tasks-filters.spec.ts                 (250+ lines)
│   ├── tasks-recurring.spec.ts               (200+ lines)
│   └── playwright.config.ts
├── vitest.config.ts
└── playwright.config.ts
```

---

## Configuration Files

### vitest.config.ts
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['__tests__/setup.ts'],
    coverage: {
      provider: 'c8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        '__tests__/',
        '.next/',
        'out/',
        '*.config.*',
      ],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
```

### __tests__/setup.ts
```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: vi.fn(),
      replace: vi.fn(),
      prefetch: vi.fn(),
      back: vi.fn(),
    };
  },
  usePathname() {
    return '/';
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock environment variables
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
```

### playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## API Mocking with MSW

### __tests__/mocks/handlers.ts
```typescript
import { http, HttpResponse } from 'msw';

export const handlers = [
  // Auth handlers
  http.post('http://localhost:8000/api/auth/login', async ({ request }) => {
    const body = await request.json();

    if (body.email === 'test@example.com' && body.password === 'TestPass123!') {
      return HttpResponse.json({
        user: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
        },
        token: 'mock-jwt-token',
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }

    return HttpResponse.json(
      { error: 'Invalid email or password' },
      { status: 401 }
    );
  }),

  // Task handlers
  http.get('http://localhost:8000/api/:userId/tasks', ({ params }) => {
    return HttpResponse.json({
      tasks: [
        {
          id: 'task-1',
          user_id: params.userId,
          title: 'Test Task',
          description: 'Test Description',
          completed: false,
          priority: 'HIGH',
          tags: ['work'],
          due_date: null,
          is_recurring: false,
          recurrence_pattern: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: null,
        },
      ],
      pagination: {
        page: 1,
        limit: 20,
        total: 1,
        total_pages: 1,
      },
    });
  }),

  http.post('http://localhost:8000/api/:userId/tasks', async ({ request, params }) => {
    const body = await request.json();

    return HttpResponse.json(
      {
        id: 'new-task-id',
        user_id: params.userId,
        ...body,
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        completed_at: null,
      },
      { status: 201 }
    );
  }),
];
```

### __tests__/mocks/server.ts
```typescript
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

---

## Component Tests

### Authentication Form Tests

#### __tests__/components/auth/LoginForm.test.tsx
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '@/components/auth/LoginForm';
import { server } from '@/__tests__/mocks/server';
import { http, HttpResponse } from 'msw';

describe('LoginForm', () => {
  beforeEach(() => {
    server.resetHandlers();
  });

  it('renders login form with email and password fields', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);

    expect(await screen.findByText(/valid email/i)).toBeInTheDocument();
  });

  it('requires password field', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);

    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'TestPass123!');
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/logging in/i)).toBeInTheDocument();
  });

  it('calls onSuccess callback with user data on successful login', async () => {
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<LoginForm onSuccess={onSuccess} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'TestPass123!');
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(
        expect.objectContaining({
          email: 'test@example.com',
          name: 'Test User',
        })
      );
    });
  });

  it('displays error message on invalid credentials', async () => {
    server.use(
      http.post('http://localhost:8000/api/auth/login', () => {
        return HttpResponse.json(
          { error: 'Invalid email or password' },
          { status: 401 }
        );
      })
    );

    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'wrong@example.com');
    await user.type(passwordInput, 'WrongPass123!');
    await user.click(submitButton);

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });

  it('stores JWT token in localStorage on successful login', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'TestPass123!');
    await user.click(submitButton);

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('mock-jwt-token');
    });
  });

  it('is keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    // Tab through form fields
    await user.tab();
    expect(screen.getByLabelText(/email/i)).toHaveFocus();

    await user.tab();
    expect(screen.getByLabelText(/password/i)).toHaveFocus();

    await user.tab();
    expect(screen.getByRole('button', { name: /log in/i })).toHaveFocus();
  });

  it('has proper ARIA labels for screen readers', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toHaveAttribute('aria-label');
    expect(screen.getByLabelText(/password/i)).toHaveAttribute('aria-label');
  });
});
```

### Task Component Tests

#### __tests__/components/tasks/TaskCard.test.tsx
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskCard } from '@/components/tasks/TaskCard';
import type { Task } from '@/lib/types';

const mockTask: Task = {
  id: 'task-1',
  user_id: 'user-123',
  title: 'Test Task',
  description: 'Test Description',
  completed: false,
  priority: 'HIGH',
  tags: ['work', 'urgent'],
  due_date: '2026-01-15T14:30:00Z',
  is_recurring: false,
  recurrence_pattern: null,
  created_at: '2026-01-01T10:00:00Z',
  updated_at: '2026-01-01T10:00:00Z',
  completed_at: null,
};

describe('TaskCard', () => {
  it('renders task with title and description', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('displays priority badge with correct color', () => {
    render(<TaskCard task={mockTask} />);

    const badge = screen.getByText('HIGH');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-red-500'); // HIGH = red
  });

  it('displays tags as chips', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText('work')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('displays formatted due date', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText(/Jan 15, 2026/i)).toBeInTheDocument();
  });

  it('shows recurring indicator for recurring tasks', () => {
    const recurringTask = { ...mockTask, is_recurring: true, recurrence_pattern: 'WEEKLY' as const };
    render(<TaskCard task={recurringTask} />);

    expect(screen.getByTitle(/recurring/i)).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', async () => {
    const onToggle = vi.fn();
    const user = userEvent.setup();
    render(<TaskCard task={mockTask} onToggle={onToggle} />);

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    expect(onToggle).toHaveBeenCalledWith('task-1');
  });

  it('calls onEdit when edit button is clicked', async () => {
    const onEdit = vi.fn();
    const user = userEvent.setup();
    render(<TaskCard task={mockTask} onEdit={onEdit} />);

    const editButton = screen.getByRole('button', { name: /edit/i });
    await user.click(editButton);

    expect(onEdit).toHaveBeenCalledWith('task-1');
  });

  it('calls onDelete when delete button is clicked', async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    render(<TaskCard task={mockTask} onDelete={onDelete} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith('task-1');
  });

  it('shows completed styling when task is complete', () => {
    const completedTask = { ...mockTask, completed: true };
    render(<TaskCard task={completedTask} />);

    const title = screen.getByText('Test Task');
    expect(title).toHaveClass('line-through');
  });

  it('truncates long descriptions', () => {
    const longDescription = 'A'.repeat(500);
    const longTask = { ...mockTask, description: longDescription };
    render(<TaskCard task={longTask} />);

    const description = screen.getByText(/A{1,}/);
    expect(description.textContent?.length).toBeLessThan(longDescription.length);
  });

  it('is keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<TaskCard task={mockTask} onToggle={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />);

    // Tab to checkbox
    await user.tab();
    expect(screen.getByRole('checkbox')).toHaveFocus();

    // Tab to edit button
    await user.tab();
    expect(screen.getByRole('button', { name: /edit/i })).toHaveFocus();

    // Tab to delete button
    await user.tab();
    expect(screen.getByRole('button', { name: /delete/i })).toHaveFocus();
  });

  it('has proper ARIA labels', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByRole('checkbox')).toHaveAttribute('aria-label', /mark task as complete/i);
    expect(screen.getByRole('button', { name: /edit/i })).toHaveAttribute('aria-label');
    expect(screen.getByRole('button', { name: /delete/i })).toHaveAttribute('aria-label');
  });

  it('applies glassmorphism styling', () => {
    const { container } = render(<TaskCard task={mockTask} />);

    const card = container.firstChild;
    expect(card).toHaveClass('backdrop-blur');
  });
});
```

---

## API Client Tests

### __tests__/lib/api.test.ts
```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchTasks, createTask, updateTask, deleteTask, toggleTaskCompletion } from '@/lib/api';
import { server } from '@/__tests__/mocks/server';
import { http, HttpResponse } from 'msw';

describe('API Client', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'mock-jwt-token');
    server.listen();
  });

  afterEach(() => {
    localStorage.clear();
    server.resetHandlers();
    server.close();
  });

  describe('fetchTasks', () => {
    it('fetches tasks for authenticated user', async () => {
      const tasks = await fetchTasks('user-123');

      expect(tasks).toHaveLength(1);
      expect(tasks[0]).toHaveProperty('title', 'Test Task');
    });

    it('includes authorization header', async () => {
      let requestHeaders: Headers | undefined;

      server.use(
        http.get('http://localhost:8000/api/:userId/tasks', ({ request }) => {
          requestHeaders = request.headers;
          return HttpResponse.json({ tasks: [], pagination: {} });
        })
      );

      await fetchTasks('user-123');

      expect(requestHeaders?.get('Authorization')).toBe('Bearer mock-jwt-token');
    });

    it('throws error on 401 Unauthorized', async () => {
      server.use(
        http.get('http://localhost:8000/api/:userId/tasks', () => {
          return HttpResponse.json({ error: 'Unauthorized' }, { status: 401 });
        })
      );

      await expect(fetchTasks('user-123')).rejects.toThrow('Unauthorized');
    });

    it('supports filtering by status', async () => {
      let requestUrl: URL | undefined;

      server.use(
        http.get('http://localhost:8000/api/:userId/tasks', ({ request }) => {
          requestUrl = new URL(request.url);
          return HttpResponse.json({ tasks: [], pagination: {} });
        })
      );

      await fetchTasks('user-123', { status: 'completed' });

      expect(requestUrl?.searchParams.get('status')).toBe('completed');
    });
  });

  describe('createTask', () => {
    it('creates task with valid data', async () => {
      const task = await createTask('user-123', {
        title: 'New Task',
        description: 'New Description',
        priority: 'HIGH',
      });

      expect(task).toHaveProperty('id');
      expect(task.title).toBe('New Task');
    });

    it('validates required title field', async () => {
      server.use(
        http.post('http://localhost:8000/api/:userId/tasks', () => {
          return HttpResponse.json(
            { error: 'Validation Error', details: { title: 'Title is required' } },
            { status: 400 }
          );
        })
      );

      await expect(
        createTask('user-123', { title: '', description: 'Test' })
      ).rejects.toThrow();
    });
  });

  describe('toggleTaskCompletion', () => {
    it('toggles task completion status', async () => {
      const result = await toggleTaskCompletion('user-123', 'task-1');

      expect(result).toHaveProperty('task');
      expect(result.task.completed).toBe(true);
    });

    it('returns new recurring task when completing recurring task', async () => {
      server.use(
        http.patch('http://localhost:8000/api/:userId/tasks/:taskId/complete', () => {
          return HttpResponse.json({
            task: { id: 'task-1', completed: true },
            new_recurring_task: { id: 'task-2', due_date: '2026-01-10T09:00:00Z' },
          });
        })
      );

      const result = await toggleTaskCompletion('user-123', 'task-1');

      expect(result.new_recurring_task).toBeDefined();
      expect(result.new_recurring_task?.id).toBe('task-2');
    });
  });
});
```

---

## Custom Hook Tests

### __tests__/hooks/useTasks.test.ts
```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useTasks } from '@/hooks/useTasks';
import { server } from '@/__tests__/mocks/server';

describe('useTasks', () => {
  it('fetches tasks on mount', async () => {
    const { result } = renderHook(() => useTasks('user-123'));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.tasks).toHaveLength(1);
    });
  });

  it('handles fetch error', async () => {
    server.use(
      http.get('http://localhost:8000/api/:userId/tasks', () => {
        return HttpResponse.json({ error: 'Server Error' }, { status: 500 });
      })
    );

    const { result } = renderHook(() => useTasks('user-123'));

    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });
  });

  it('provides createTask function', async () => {
    const { result } = renderHook(() => useTasks('user-123'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await result.current.createTask({ title: 'New Task' });

    await waitFor(() => {
      expect(result.current.tasks).toHaveLength(2);
    });
  });
});
```

---

## Running Tests

### Run Unit Tests
```bash
npm run test               # Run all unit tests
npm run test:watch        # Watch mode
npm run test:ui           # Vitest UI
npm run test:coverage     # Generate coverage report
```

### Run E2E Tests
```bash
npx playwright test                    # Run all E2E tests
npx playwright test --headed          # Run with browser visible
npx playwright test --debug           # Debug mode
npx playwright test auth.spec.ts      # Run specific file
npx playwright show-report            # View test report
```

---

## Success Criteria

Frontend testing is complete when:

- ✅ 70%+ overall test coverage
- ✅ 90%+ coverage for authentication components
- ✅ 90%+ coverage for task components
- ✅ All E2E critical flows passing
- ✅ All accessibility tests passing
- ✅ Cross-browser compatibility verified (Chrome, Firefox, Safari)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
