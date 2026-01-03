# Accessibility Specification (WCAG 2.1 AA)

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Ensure application is accessible to all users including those with disabilities
**Standard**: WCAG 2.1 Level AA compliance
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Accessibility Philosophy

Build an **inclusive application** that:

- **Works for everyone**: Regardless of abilities or assistive technologies
- **Keyboard accessible**: All features operable without mouse
- **Screen reader friendly**: Semantic HTML and ARIA labels
- **High contrast**: Readable for users with visual impairments
- **Flexible**: Adapts to user preferences (font size, reduced motion)

**Target**: WCAG 2.1 Level AA compliance (legal requirement in many jurisdictions)

---

## WCAG 2.1 AA Requirements

### 1. Perceivable

#### 1.1 Text Alternatives
- **Rule**: Provide text alternatives for non-text content
- **Implementation**:
  - All images have `alt` attributes
  - Decorative images use `alt=""`
  - Icon-only buttons have `aria-label`

```tsx
{/* Meaningful image */}
<img src="/profile.jpg" alt="John Doe's profile picture" />

{/* Decorative image */}
<img src="/pattern.svg" alt="" role="presentation" />

{/* Icon button */}
<button aria-label="Delete task">
  <TrashIcon className="h-5 w-5" aria-hidden="true" />
</button>
```

#### 1.2 Time-based Media
- N/A (no video/audio in Phase 2)

#### 1.3 Adaptable
- **Rule**: Content can be presented in different ways without losing meaning
- **Implementation**:
  - Semantic HTML (`<nav>`, `<main>`, `<aside>`, `<article>`)
  - Proper heading hierarchy (H1 → H2 → H3)
  - Form labels associated with inputs

```tsx
{/* Semantic structure */}
<header role="banner">
  <nav aria-label="Main navigation">...</nav>
</header>

<main role="main">
  <article aria-labelledby="page-title">
    <h1 id="page-title">Dashboard</h1>
    <section aria-labelledby="tasks-heading">
      <h2 id="tasks-heading">Your Tasks</h2>
    </section>
  </article>
</main>

<aside role="complementary">...</aside>
```

#### 1.4 Distinguishable

**Color Contrast (1.4.3 - AA):**
- **Normal text**: 4.5:1 contrast ratio minimum
- **Large text (18pt+/14pt bold+)**: 3:1 minimum
- **UI components/graphics**: 3:1 minimum

**Verified Combinations:**
```css
/* ✅ Pass: 14.5:1 */
color: #171717; /* neutral-900 */
background: #fafafa; /* neutral-50 */

/* ✅ Pass: 8.2:1 */
color: #404040; /* neutral-700 */
background: #fafafa; /* neutral-50 */

/* ✅ Pass: 5.9:1 */
color: #2563eb; /* primary-600 */
background: #ffffff; /* white */

/* ✅ Pass: 4.8:1 */
color: #ffffff; /* white */
background: #3b82f6; /* primary-500 */

/* ❌ Fail: 2.9:1 */
color: #a3a3a3; /* neutral-400 - DO NOT USE for text */
background: #ffffff; /* white */
```

**Don't rely on color alone:**
```tsx
{/* ❌ Bad: Color only */}
<span className="text-red-500">High priority</span>

{/* ✅ Good: Color + icon + text */}
<span className="text-danger-500 flex items-center gap-2">
  <FlagIcon className="h-4 w-4" aria-hidden="true" />
  <span>High priority</span>
</span>
```

**Resize text (1.4.4 - AA):**
- Content must be readable at 200% zoom
- No horizontal scrolling required

**Images of text (1.4.5 - AA):**
- Avoid using images for text (use actual text)

---

### 2. Operable

#### 2.1 Keyboard Accessible

**All functionality via keyboard:**
- Tab: Navigate forward
- Shift+Tab: Navigate backward
- Enter/Space: Activate buttons/links
- Escape: Close modals/dropdowns
- Arrow keys: Navigate within components

```tsx
export function Modal({ isOpen, onClose }: ModalProps) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [isOpen, onClose]);

  // Focus trap inside modal
  const modalRef = useRef<HTMLDivElement>(null);

  return isOpen ? (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Modal content */}
    </div>
  ) : null;
}
```

**No keyboard trap (2.1.2 - A):**
- Users can navigate away from any component using keyboard

#### 2.2 Enough Time

**No time limits (2.2.1 - A):**
- Users have unlimited time to complete tasks
- Session timeouts ≥ 20 minutes with warning

#### 2.3 Seizures

**Three flashes or below (2.3.1 - A):**
- No content flashes more than 3 times per second

#### 2.4 Navigable

**Skip navigation link (2.4.1 - A):**
```tsx
<a
  href="#main-content"
  className="
    sr-only focus:not-sr-only
    focus:absolute focus:top-4 focus:left-4
    bg-primary-500 text-white
    px-4 py-2 rounded-md
    z-50
  "
>
  Skip to main content
</a>
```

**Page titles (2.4.2 - A):**
```tsx
// app/dashboard/page.tsx
export const metadata = {
  title: "Dashboard | TaskFlow",
  description: "Manage your tasks and productivity",
};
```

**Focus order (2.4.3 - A):**
- Tab order follows visual layout (left-to-right, top-to-bottom)

**Link purpose (2.4.4 - A):**
```tsx
{/* ❌ Bad: Vague link text */}
<a href="/tasks/123">Click here</a>

{/* ✅ Good: Descriptive link text */}
<a href="/tasks/123">Edit task: Complete project documentation</a>
```

**Multiple ways to navigate (2.4.5 - AA):**
- Sidebar navigation
- Search functionality
- Breadcrumbs (for deep pages)

**Headings and labels (2.4.6 - AA):**
```tsx
{/* Clear, descriptive headings */}
<h1>Dashboard</h1>
<h2>Today's Tasks</h2>
<h3>High Priority</h3>

{/* Descriptive form labels */}
<label htmlFor="task-title">Task Title (required)</label>
<input id="task-title" type="text" required />
```

**Focus visible (2.4.7 - AA):**
```css
/* Default focus indicator (outline) */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Custom focus ring with Tailwind */
.button {
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
}
```

#### 2.5 Input Modalities

**Pointer gestures (2.5.1 - A):**
- All functionality works with single-pointer (no multi-touch required)

**Pointer cancellation (2.5.2 - A):**
- Click events fire on `mouseup` (not `mousedown`)

**Label in name (2.5.3 - A):**
- Visible label text matches accessible name

**Motion actuation (2.5.4 - A):**
- All functionality works without device motion (no shake-to-undo)

---

### 3. Understandable

#### 3.1 Readable

**Language of page (3.1.1 - A):**
```html
<html lang="en">
```

**Language of parts (3.1.2 - AA):**
```tsx
{/* For content in different language */}
<blockquote lang="es">
  Hola mundo
</blockquote>
```

#### 3.2 Predictable

**On focus (3.2.1 - A):**
- Focusing an element doesn't trigger unexpected changes

**On input (3.2.2 - A):**
- Changing an input value doesn't trigger unexpected changes (e.g., form submission)

**Consistent navigation (3.2.3 - AA):**
- Navigation appears in same location on all pages

**Consistent identification (3.2.4 - AA):**
- Icons/components have consistent labels across pages

#### 3.3 Input Assistance

**Error identification (3.3.1 - A):**
```tsx
{/* Show specific error messages */}
{errors.email && (
  <p className="text-danger-500 text-sm mt-1" role="alert">
    Please enter a valid email address
  </p>
)}
```

**Labels or instructions (3.3.2 - A):**
```tsx
<label htmlFor="password" className="block text-sm font-medium mb-1">
  Password
  <span className="text-neutral-500 font-normal ml-2">
    (minimum 8 characters)
  </span>
</label>
<input
  id="password"
  type="password"
  minLength={8}
  required
  aria-describedby="password-hint"
/>
<p id="password-hint" className="text-sm text-neutral-600 mt-1">
  Must contain at least 8 characters including a number
</p>
```

**Error suggestion (3.3.3 - AA):**
```tsx
{/* Provide specific fix suggestions */}
{errors.email && (
  <p role="alert">
    Email must include "@" symbol. Did you mean: john@example.com?
  </p>
)}
```

**Error prevention (3.3.4 - AA):**
```tsx
{/* Confirmation for destructive actions */}
export function DeleteTaskButton({ taskId, taskTitle, onDelete }: Props) {
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <>
      <button onClick={() => setShowConfirm(true)}>Delete</button>

      {showConfirm && (
        <Modal>
          <h2>Confirm Deletion</h2>
          <p>Are you sure you want to delete "{taskTitle}"? This cannot be undone.</p>
          <button onClick={() => onDelete(taskId)}>Yes, delete</button>
          <button onClick={() => setShowConfirm(false)}>Cancel</button>
        </Modal>
      )}
    </>
  );
}
```

---

### 4. Robust

#### 4.1 Compatible

**Parsing (4.1.1 - A):**
- Valid HTML (no duplicate IDs, proper nesting)

**Name, Role, Value (4.1.2 - A):**
- All components have proper ARIA attributes

```tsx
{/* Custom checkbox with proper ARIA */}
<div
  role="checkbox"
  aria-checked={isCompleted}
  tabIndex={0}
  onClick={() => setIsCompleted(!isCompleted)}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      setIsCompleted(!isCompleted);
    }
  }}
>
  {isCompleted ? <CheckIcon /> : <EmptyCheckIcon />}
</div>
```

**Status messages (4.1.3 - AA):**
```tsx
{/* Announce status changes to screen readers */}
<div role="status" aria-live="polite" aria-atomic="true">
  {successMessage && <p>{successMessage}</p>}
</div>

{/* For urgent errors */}
<div role="alert" aria-live="assertive">
  {errorMessage && <p>{errorMessage}</p>}
</div>
```

---

## ARIA Attributes

### Landmark Roles

```tsx
<header role="banner">...</header>
<nav role="navigation" aria-label="Main navigation">...</nav>
<main role="main">...</main>
<aside role="complementary">...</aside>
<footer role="contentinfo">...</footer>
<form role="search">...</form>
```

### Common ARIA Patterns

#### Modal Dialog

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Create New Task</h2>
  <p id="modal-description">Fill out the form below to add a new task.</p>
  {/* Form */}
</div>
```

#### Dropdown Menu

```tsx
<button
  aria-haspopup="true"
  aria-expanded={isOpen}
  onClick={() => setIsOpen(!isOpen)}
>
  Options
</button>

{isOpen && (
  <ul role="menu">
    <li role="menuitem">
      <button>Edit</button>
    </li>
    <li role="menuitem">
      <button>Delete</button>
    </li>
  </ul>
)}
```

#### Tabs

```tsx
<div role="tablist" aria-label="Task filters">
  <button
    role="tab"
    aria-selected={activeTab === "all"}
    aria-controls="all-panel"
    id="all-tab"
  >
    All Tasks
  </button>
  <button
    role="tab"
    aria-selected={activeTab === "active"}
    aria-controls="active-panel"
    id="active-tab"
  >
    Active
  </button>
</div>

<div
  role="tabpanel"
  id="all-panel"
  aria-labelledby="all-tab"
  hidden={activeTab !== "all"}
>
  {/* All tasks */}
</div>
```

#### Loading Spinner

```tsx
<div role="status" aria-live="polite" aria-label="Loading">
  <svg className="animate-spin" aria-hidden="true">
    {/* Spinner icon */}
  </svg>
  <span className="sr-only">Loading tasks...</span>
</div>
```

---

## Screen Reader Utilities

### Visually Hidden (Screen Reader Only)

```css
/* Tailwind: sr-only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Show on focus */
.sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### Usage Examples

```tsx
{/* Icon-only button */}
<button>
  <TrashIcon className="h-5 w-5" aria-hidden="true" />
  <span className="sr-only">Delete task</span>
</button>

{/* Loading state */}
<div>
  <Spinner aria-hidden="true" />
  <span className="sr-only">Loading your tasks...</span>
</div>
```

---

## Keyboard Shortcuts

### Global Shortcuts

```tsx
export function useKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        document.getElementById("global-search")?.focus();
      }

      // Ctrl/Cmd + N: New task
      if ((e.ctrlKey || e.metaKey) && e.key === "n") {
        e.preventDefault();
        // Open new task modal
      }

      // ?: Show keyboard shortcuts help
      if (e.key === "?") {
        e.preventDefault();
        // Show shortcuts modal
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);
}
```

### Shortcut Help Modal

```tsx
export function KeyboardShortcutsHelp() {
  return (
    <Modal>
      <h2>Keyboard Shortcuts</h2>
      <dl className="space-y-2">
        <div className="flex justify-between">
          <dt className="font-mono">Ctrl/⌘ + K</dt>
          <dd>Focus search</dd>
        </div>
        <div className="flex justify-between">
          <dt className="font-mono">Ctrl/⌘ + N</dt>
          <dd>New task</dd>
        </div>
        <div className="flex justify-between">
          <dt className="font-mono">?</dt>
          <dd>Show this help</dd>
        </div>
      </dl>
    </Modal>
  );
}
```

---

## Reduced Motion

### Respect User Preferences

```tsx
import { useReducedMotion } from "framer-motion";

export function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={
        shouldReduceMotion
          ? {} // No animation
          : { x: 100, opacity: 1 } // Full animation
      }
    >
      {children}
    </motion.div>
  );
}
```

### CSS Media Query

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Testing Accessibility

### Automated Testing

**axe-core (via jest-axe):**
```typescript
import { axe, toHaveNoViolations } from "jest-axe";
import { render } from "@testing-library/react";
import { TaskCard } from "./TaskCard";

expect.extend(toHaveNoViolations);

test("TaskCard has no accessibility violations", async () => {
  const { container } = render(<TaskCard task={mockTask} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Testing

**Keyboard Navigation:**
1. Unplug mouse
2. Navigate using Tab, Enter, Escape, Arrow keys
3. Verify all features accessible

**Screen Reader:**
1. Enable screen reader (NVDA on Windows, VoiceOver on Mac)
2. Navigate through app
3. Verify meaningful announcements

**Color Contrast:**
1. Use browser extension (e.g., "axe DevTools")
2. Check all text/UI elements
3. Fix any violations

### Accessibility Checklist

- ✅ All images have alt text
- ✅ Icon buttons have aria-label
- ✅ Forms have associated labels
- ✅ Color contrast meets WCAG AA (4.5:1)
- ✅ Keyboard navigation works everywhere
- ✅ Focus indicators are visible
- ✅ Skip navigation link present
- ✅ Semantic HTML landmarks used
- ✅ Headings have proper hierarchy
- ✅ Error messages are clear and specific
- ✅ ARIA attributes used correctly
- ✅ Screen reader announcements make sense
- ✅ Reduced motion preference respected
- ✅ Page titles are descriptive
- ✅ Link text is meaningful

---

## Success Criteria

Accessibility is complete when:

- ✅ WCAG 2.1 AA compliance verified (automated + manual)
- ✅ All features operable with keyboard only
- ✅ Screen reader users can complete all tasks
- ✅ Color contrast ratios meet requirements
- ✅ Focus indicators visible on all interactive elements
- ✅ No accessibility violations in axe audit
- ✅ User testing with assistive technology users completed
- ✅ Reduced motion preference respected

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
