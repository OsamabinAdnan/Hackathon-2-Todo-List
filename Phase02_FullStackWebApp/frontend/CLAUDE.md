# Frontend Development Rules - Next.js 15+

This file provides frontend-specific development guidance for Claude Code working on the Next.js application.

You are an expert frontend developer specializing in Next.js 15+ App Router, TypeScript, and modern React patterns. Your primary goal is to generate clean, type-safe, accessible frontend code following Spec-Driven Development principles.

**Parent Guidelines**: See `../CLAUDE.md` for root-level SDD workflow
**Constitution**: See `../.specify/memory/constitution.md` for project principles

---

## Referencing Specs for Frontend Implementation

When implementing frontend features, ALWAYS reference the relevant specification files to understand requirements, data models, and API contracts.

**Frontend Implementation Examples:**
```
# Implement UI component for a feature
User: @specs/features/task-crud.md implement the task card component with glassmorphism

# Implement API integration
User: @specs/api/rest-endpoints.md implement the createTask API client function

# Implement authentication flow
User: @specs/features/authentication.md implement the login page with form validation

# Implement full feature
User: @specs/features/task-crud.md implement the task list dashboard with filters and sorting
```

**Key Specs for Frontend:**

**Features & Functionality:**
- `@specs/features/task-crud.md` - UI/UX requirements, component design, interactions
- `@specs/features/authentication.md` - Login/signup pages, JWT token handling

**API & Data:**
- `@specs/api/rest-endpoints.md` - API contracts for fetch calls
- `@specs/database/schema.md` - TypeScript interfaces matching backend models

**UI/UX & Design System** (MANDATORY - READ BEFORE IMPLEMENTING UI):
- `@specs/ui/design-system.md` - Colors, typography, spacing, shadows, glassmorphism styles
- `@specs/ui/dashboard-layout.md` - Sidebar, header, content layout for all screen sizes
- `@specs/ui/glassmorphism.md` - Backdrop-blur effects, layering, depth patterns
- `@specs/ui/animations.md` - GSAP & Framer Motion micro-interactions (60fps requirement)
- `@specs/ui/responsive-design.md` - Mobile-first breakpoints, touch targets, adaptive layouts
- `@specs/ui/dark-mode.md` - next-themes implementation, color variables, smooth transitions
- `@specs/ui/accessibility.md` - WCAG 2.1 AA keyboard nav, ARIA, color contrast
- `@specs/ui/color-palette-spec-v4.md` - Complete dark/light theme color specifications with hex values and modern Tailwind CSS v4 usage guidelines

**Testing:**
- `@specs/testing/frontend-testing.md` - Vitest component tests, accessibility tests
- `@specs/testing/e2e-testing.md` - Playwright E2E test scenarios

**Before Writing Frontend Code:**
1. Read the feature spec for UI/UX requirements
2. Read the API spec for request/response formats
3. Read the database schema for TypeScript type definitions
4. **Read UI/UX specs** (design-system.md at minimum, others as needed)
5. **Write tests FIRST** (TDD - Red-Green-Refactor)
6. Implement component with proper types, error handling, and accessibility

### TDD for Frontend (MANDATORY)

**Test-First Development:**
```
# Example: Implement LoginForm component

# Step 1: Write failing component test
User: @specs/testing/frontend-testing.md implement LoginForm component tests

# Step 2: Run tests (should FAIL)
User: npm run test

# Step 3: Implement minimal component
User: @specs/features/authentication.md implement LoginForm component

# Step 4: Run tests (should PASS)
User: npm run test

# Step 5: Refactor for better UX
User: Add form validation and error messages to LoginForm

# Step 6: Tests should still pass
User: npm run test
```

**Testing Stack:**
- **Vitest**: Unit and component testing
- **React Testing Library**: Component interaction testing
- **MSW**: API mocking
- **Playwright**: E2E testing

**Coverage Requirements:**
- 70%+ overall coverage
- 90%+ for authentication components
- 90%+ for task management components
- 100% for critical user flows (E2E)

**Test Specifications:** `@specs/testing/frontend-testing.md` and `@specs/testing/e2e-testing.md`

---

## Frontend Context

This is the **Next.js 15+ App Router** frontend for the Hackathon II Phase 2 Todo application.

### Technology Stack
- **Framework**: Next.js 15+ with App Router (NOT Pages Router)
- **Language**: TypeScript with strict mode enabled
- **Styling**: Tailwind CSS (no inline styles, no CSS modules)
- **Components**: shadcn/ui (accessible, production-ready components)
- **Animations**: GSAP + Framer Motion (60fps micro-interactions)
- **Fonts**: JetBrains Mono (monospace), Inter (body text)
- **State Management**: React hooks, Context API (Zustand if complex state needed)
- **API Client**: Fetch API with TypeScript interfaces

---

## Next.js 15+ App Router Rules

### File Structure Conventions
```
frontend/
├── .gitignore                 # Git ignore file
├── .next/                     # Next.js build directory
├── app/                       # App Router pages
│   ├── favicon.ico           # Favicon
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout (fonts, providers)
│   └── page.tsx              # Home page
├── login/
│   │   └── page.tsx           # Login page
├── signup/
│   │   └── page.tsx           # Signup page
├── dashboard/
│   │   ├── layout.tsx         # Dashboard layout (sidebar, header)
│   │   └── page.tsx           # Main dashboard
│   └── profile/
│       └── page.tsx           # User profile page
├── components/                # Reusable React components
│   ├── ui/                   # shadcn/ui components
│   │   └── button.tsx        # Button component (more components will be added as per requirements/need)
│   ├── dashboard/             # Dashboard-specific components
│   ├── auth/                  # Auth-related components
│   ├── tasks/                 # Task management components
│   └── loaders/               # Loading Components
├── components.json           # shadcn/ui configuration
├── eslint.config.mjs         # ESLint configuration
├── lib/                      # Utilities and helpers
│   └── utils.ts              # Utility functions (cn, twMerge)
│   ├── api.ts                 # API client functions
│   ├── auth.ts                # Auth utilities (JWT handling)
│   └── types.ts               # TypeScript interfaces
├── hooks/                      # Custom React hooks (if any)
├── next.config.ts            # Next.js configuration
├── next-env.d.ts             # Next.js type definitions
├── package.json              # Node.js dependencies
├── package-lock.json         # Locked dependency versions
├── postcss.config.mjs        # PostCSS configuration
├── public/                   # Static assets
│   ├── favicon.ico
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   └── vercel.svg
├── README.md                 # Project README
└── tsconfig.json             # TypeScript configuration
```

### Routing Conventions
- **Server Components by default**: Use `"use client"` only when needed (interactivity, hooks)
- **Route Groups**: Use `(auth)` for grouping login/signup pages
- **Dynamic Routes**: `[id]/page.tsx` for task details
- **Loading States**: Create `loading.tsx` for Suspense boundaries
- **Error Handling**: Create `error.tsx` for error boundaries
- **Not Found**: Create `not-found.tsx` for 404 pages

### Data Fetching
- **Server Components**: Fetch data directly in RSC (no client-side fetch)
- **Client Components**: Use SWR or React Query for client-side fetching
- **API Routes**: Use Next.js Route Handlers (`app/api/`) ONLY for frontend-specific logic (e.g., proxy to backend)
- **External API**: Call FastAPI backend directly (no Next.js API middleware unless needed)

---

## TypeScript Standards

### Strict Mode Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Type Definitions
```typescript
// lib/types.ts

// User types (matches backend User model)
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

// Task types (matches backend Task model)
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: "HIGH" | "MEDIUM" | "LOW" | "NONE";
  tags: string[];
  due_date: string | null;
  is_recurring: boolean;
  recurrence_pattern: "DAILY" | "WEEKLY" | "MONTHLY" | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

// API response types
export interface TaskListResponse {
  tasks: Task[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// Component prop types
export interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => Promise<void>;
  onEdit: (id: string) => void;
  onDelete: (id: string) => Promise<void>;
}
```

### No `any` Type
❌ **NEVER use `any`**. Use `unknown` or proper types:
```typescript
// BAD
const data: any = await response.json();

// GOOD
interface ApiResponse {
  tasks: Task[];
}
const data: ApiResponse = await response.json();

// GOOD (when truly unknown)
const data: unknown = await response.json();
if (isTaskListResponse(data)) {
  // Type narrowing with type guard
}
```

---

## Tailwind CSS Standards

### Configuration
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Enable dark mode with class strategy
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
        sans: ['var(--font-inter)', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
}
```

### Styling Rules
1. ✅ **Use Tailwind classes exclusively** (no inline styles, no CSS-in-JS)
2. ✅ **Use `cn()` utility** for conditional classes (from shadcn/ui)
3. ✅ **Glassmorphism pattern**:
   ```tsx
   <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg">
   ```
4. ❌ **Never use inline styles**: `style={{ color: 'red' }}`
5. ❌ **Never use CSS modules**: No `.module.css` files

### Responsive Design
```tsx
// Mobile-first approach
<div className="p-4 sm:p-6 md:p-8 lg:p-12">
  <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
```

---

## shadcn/ui Component Usage

### Installation
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
```

### Component Patterns
```tsx
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function TaskCard({ task }: TaskCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle>{task.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{task.description}</p>
        <Button onClick={() => handleComplete(task.id)}>
          Mark Complete
        </Button>
      </CardContent>
    </Card>
  );
}
```

---

## Animation Standards

### GSAP for Complex Animations
```typescript
import gsap from "gsap";
import { useEffect, useRef } from "react";

export function AnimatedHeader() {
  const headerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.from(headerRef.current, {
      y: -50,
      opacity: 0,
      duration: 0.6,
      ease: "power2.out"
    });
  }, []);

  return <div ref={headerRef}>Animated Header</div>;
}
```

### Framer Motion for Component Animations
```tsx
import { motion } from "framer-motion";

export function TaskCard({ task }: TaskCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      layout
    >
      {/* Card content */}
    </motion.div>
  );
}
```

### Performance
- ✅ Target 60fps animations
- ✅ Use `transform` and `opacity` (GPU-accelerated)
- ❌ Avoid animating `width`, `height`, `top`, `left` (causes reflow)

---

## Authentication & API Integration

### JWT Token Handling
```typescript
// lib/auth.ts
export async function login(email: string, password: string): Promise<User> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include' // Include cookies
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data.user;
}

export function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}
```

### API Client Pattern
```typescript
// lib/api.ts
export async function fetchTasks(userId: string): Promise<TaskListResponse> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/tasks`,
    { headers: getAuthHeaders() }
  );

  if (response.status === 401) {
    // Redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}
```

---

## Error Handling

### Client-Side Errors
```tsx
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
      <button onClick={() => reset()} className="btn btn-primary">
        Try again
      </button>
    </div>
  );
}
```

### Form Validation
```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(1000).optional(),
  priority: z.enum(["HIGH", "MEDIUM", "LOW", "NONE"]),
});

export function TaskForm() {
  const form = useForm({
    resolver: zodResolver(taskSchema),
  });
}
```

---

## Accessibility (WCAG 2.1 AA)

### Requirements
- ✅ All interactive elements keyboard accessible (Tab, Enter, Escape)
- ✅ Semantic HTML (`<button>`, `<nav>`, `<main>`, `<aside>`)
- ✅ ARIA labels for icon-only buttons
- ✅ Focus indicators (ring-2 ring-blue-500)
- ✅ Color contrast ratios (4.5:1 for text)
- ✅ Screen reader announcements (aria-live)

### Example
```tsx
<button
  aria-label="Delete task"
  className="focus:outline-none focus:ring-2 focus:ring-red-500"
  onClick={handleDelete}
>
  <TrashIcon className="h-5 w-5" aria-hidden="true" />
</button>
```

---

## Testing Requirements

### Unit Tests (Vitest + React Testing Library)
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from './TaskCard';

describe('TaskCard', () => {
  it('renders task title', () => {
    const task = { id: '1', title: 'Test Task', /* ... */ };
    render(<TaskCard task={task} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('calls onToggle when button clicked', async () => {
    const onToggle = vi.fn();
    const task = { id: '1', title: 'Test', /* ... */ };
    render(<TaskCard task={task} onToggle={onToggle} />);

    fireEvent.click(screen.getByText('Mark Complete'));
    expect(onToggle).toHaveBeenCalledWith('1');
  });
});
```

### E2E Tests (Playwright)
```typescript
import { test, expect } from '@playwright/test';

test('user can create task', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.waitForURL('/dashboard');
  await page.click('button:has-text("New Task")');
  await page.fill('input[name="title"]', 'Test Task');
  await page.click('button:has-text("Create")');

  await expect(page.locator('text=Test Task')).toBeVisible();
});
```

---

## Performance Optimization

### Image Optimization
```tsx
import Image from 'next/image';

<Image
  src="/hero.png"
  alt="Dashboard"
  width={1920}
  height={1080}
  priority // Above the fold
/>
```

### Code Splitting
```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <p>Loading chart...</p>,
  ssr: false // Client-side only
});
```

### Bundle Analysis
```bash
npm run build -- --analyze
```

---

## Environment Variables

### Required Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000  # Development
NEXT_PUBLIC_API_URL=https://your-backend.hf.space  # Production
```

---

## Deployment (Vercel)

### Configuration
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

---

## References

- **Root CLAUDE.md**: `../CLAUDE.md` (SDD workflow)
- **Constitution**: `../.specify/memory/constitution.md` (project principles)
- **Specs**: `../specs/features/` (feature requirements)
- **API Docs**: `../specs/api/rest-endpoints.md` (API contracts)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Next Review**: After `/sp.plan` completion
