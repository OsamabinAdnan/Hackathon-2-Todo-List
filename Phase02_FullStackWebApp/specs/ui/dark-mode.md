# Dark Mode Specification

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define dark mode implementation with theme toggle and smooth transitions
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Dark Mode Philosophy

Provide a **premium dark mode experience** that:

- **Reduces eye strain**: Lower brightness for extended work sessions
- **Saves power**: OLED screens use less energy with dark pixels
- **Respects preferences**: Follows system theme by default
- **Smooth transitions**: Elegant switching between themes
- **Maintains readability**: Proper contrast in both themes

---

## Implementation Strategy

### Strategy: CSS Variables + Tailwind Dark Mode Class

**Approach**: Use Tailwind's `dark:` variant with `.dark` class on `<html>` element

**Why This Approach:**
- Simple to implement
- Works with Tailwind utilities
- Easy to toggle programmatically
- No Flash of Unstyled Content (FOUC)
- Compatible with Next.js App Router

---

## Configuration

### 1. Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Use class strategy (NOT media query)
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Light mode colors (default)
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        neutral: {
          50: '#fafafa',
          900: '#171717',
        },
      },
    },
  },
};
```

### 2. Global CSS Variables

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light mode (default) */
    --background: 250 250 250; /* #fafafa */
    --foreground: 23 23 23; /* #171717 */

    --primary: 59 130 246; /* #3b82f6 */
    --primary-foreground: 255 255 255;

    --card: 255 255 255;
    --card-foreground: 23 23 23;

    --border: 229 229 229; /* #e5e5e5 */
    --input: 229 229 229;

    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
  }

  .dark {
    /* Dark mode */
    --background: 24 24 27; /* #18181b */
    --foreground: 250 250 250; /* #fafafa */

    --primary: 96 165 250; /* #60a5fa - lighter in dark mode */
    --primary-foreground: 23 23 23;

    --card: 39 39 42; /* #27272a */
    --card-foreground: 250 250 250;

    --border: 63 63 70; /* #3f3f46 */
    --input: 63 63 70;

    --glass-bg: rgba(0, 0, 0, 0.3);
    --glass-border: rgba(255, 255, 255, 0.1);
  }
}

/* Smooth color transitions */
* {
  transition: background-color 200ms ease, border-color 200ms ease, color 200ms ease;
}

/* Disable transitions on theme change to prevent jarring animations */
html.changing-theme * {
  transition: none !important;
}
```

---

## Color Palette

### Light Mode

```css
Background: #fafafa (neutral-50)
Foreground (text): #171717 (neutral-900)
Primary: #3b82f6 (primary-500)
Card background: #ffffff (white)
Border: #e5e5e5 (neutral-200)
```

### Dark Mode

```css
Background: #18181b (zinc-900)
Foreground (text): #fafafa (neutral-50)
Primary: #60a5fa (primary-400 - lighter)
Card background: #27272a (zinc-800)
Border: #3f3f46 (zinc-700)
```

### Color Adjustments for Dark Mode

**Key Differences:**
1. **Primary color**: Slightly lighter in dark mode for better contrast
2. **Background**: Very dark but not pure black (#18181b not #000000)
3. **Text**: Off-white not pure white (#fafafa not #ffffff)
4. **Borders**: Higher opacity to maintain visibility

---

## Theme Toggle Component

### Toggle Button

```tsx
'use client';

import { useTheme } from 'next-themes';
import { MoonIcon, SunIcon } from 'lucide-react';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button className="h-10 w-10 rounded-md bg-neutral-100 dark:bg-neutral-800" />
    );
  }

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="
        relative h-10 w-10 rounded-md
        bg-neutral-100 hover:bg-neutral-200
        dark:bg-neutral-800 dark:hover:bg-neutral-700
        transition-colors duration-200
        flex items-center justify-center
      "
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <SunIcon
        className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
        aria-hidden="true"
      />
      <MoonIcon
        className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
        aria-hidden="true"
      />
    </button>
  );
}
```

### Dropdown Theme Selector

```tsx
export function ThemeSelector() {
  const { theme, setTheme } = useTheme();

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value)}
      className="input"
      aria-label="Select theme"
    >
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="system">System</option>
    </select>
  );
}
```

---

## Theme Provider Setup

### Install next-themes

```bash
npm install next-themes
```

### Root Layout Configuration

```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

**Key Props:**
- `attribute="class"` - Adds `.dark` class to `<html>`
- `defaultTheme="system"` - Respects OS preference by default
- `enableSystem` - Allows "system" theme option
- `disableTransitionOnChange` - Prevents transition flash when toggling

---

## Component Styling

### Using Tailwind Dark Mode Classes

```tsx
{/* Background */}
<div className="bg-white dark:bg-zinc-900">

{/* Text */}
<p className="text-neutral-900 dark:text-neutral-50">

{/* Border */}
<div className="border border-neutral-200 dark:border-zinc-700">

{/* Glassmorphism */}
<div className="
  bg-white/10 dark:bg-black/30
  backdrop-blur-md
  border border-white/20 dark:border-white/10
">

{/* Button */}
<button className="
  bg-primary-500 hover:bg-primary-600
  dark:bg-primary-400 dark:hover:bg-primary-500
  text-white
">

{/* Card */}
<div className="
  bg-white dark:bg-zinc-800
  border border-neutral-200 dark:border-zinc-700
  rounded-lg p-6
">
```

### Using CSS Variables

```tsx
{/* Alternative: Use CSS variables for more flexibility */}
<div className="bg-[rgb(var(--background))] text-[rgb(var(--foreground))]">
  <div className="bg-[rgb(var(--card))] border-[rgb(var(--border))]">
    {/* Content */}
  </div>
</div>
```

---

## Dark Mode for Specific Components

### Task Card

```tsx
export function TaskCard({ task }: TaskCardProps) {
  return (
    <div className="
      glass-card
      bg-white/10 dark:bg-black/30
      backdrop-blur-md
      border border-white/20 dark:border-white/10
      rounded-lg p-6
      hover:shadow-xl
      transition-shadow duration-300
    ">
      <h3 className="text-neutral-900 dark:text-neutral-50 font-semibold">
        {task.title}
      </h3>
      <p className="text-neutral-600 dark:text-neutral-400 text-sm mt-2">
        {task.description}
      </p>
    </div>
  );
}
```

### Header

```tsx
export function Header() {
  return (
    <header className="
      fixed top-0 left-0 right-0
      bg-white/80 dark:bg-zinc-900/80
      backdrop-blur-md
      border-b border-neutral-200 dark:border-zinc-700
      z-20
    ">
      <div className="flex items-center justify-between px-6 h-16">
        <Logo />
        <div className="flex items-center space-x-4">
          <SearchBar />
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
```

### Modal

```tsx
export function Modal({ isOpen, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="
          absolute inset-0
          bg-black/20 dark:bg-black/40
          backdrop-blur-sm
        "
        onClick={onClose}
      />

      {/* Modal */}
      <div className="
        relative
        bg-white/70 dark:bg-zinc-900/90
        backdrop-blur-xl
        border border-white/30 dark:border-white/10
        rounded-xl p-6
        max-w-lg w-full
        shadow-2xl
      ">
        {children}
      </div>
    </div>
  );
}
```

---

## System Preference Detection

### Default to System Theme

```tsx
// next-themes automatically detects system preference
<ThemeProvider defaultTheme="system" enableSystem>
```

### Manual Detection (if needed)

```tsx
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Listen for changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  const newColorScheme = e.matches ? 'dark' : 'light';
  console.log('System theme changed to:', newColorScheme);
});
```

---

## Avoiding Flash of Unstyled Content (FOUC)

### Problem

When page loads, there's a brief moment where the wrong theme shows before JavaScript loads.

### Solution 1: next-themes Built-in

```tsx
// app/layout.tsx
<html lang="en" suppressHydrationWarning>
```

`suppressHydrationWarning` prevents React from complaining about server/client mismatch.

### Solution 2: Blocking Script (Advanced)

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                const theme = localStorage.getItem('theme') || 'system';
                const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                const appliedTheme = theme === 'system' ? systemTheme : theme;
                document.documentElement.classList.toggle('dark', appliedTheme === 'dark');
              })();
            `,
          }}
        />
      </head>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

---

## Persistence

### LocalStorage (Automatic)

next-themes automatically saves theme preference to localStorage:

```javascript
localStorage.getItem('theme'); // 'light', 'dark', or 'system'
```

### Cookie Alternative (for SSR)

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const theme = request.cookies.get('theme')?.value || 'system';
  const response = NextResponse.next();
  response.cookies.set('theme', theme);
  return response;
}
```

---

## Accessibility

### Announce Theme Change to Screen Readers

```tsx
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [announcement, setAnnouncement] = useState('');

  const handleToggle = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    setAnnouncement(`Theme changed to ${newTheme} mode`);
    setTimeout(() => setAnnouncement(''), 1000);
  };

  return (
    <>
      <button onClick={handleToggle} aria-label="Toggle theme">
        {/* Icons */}
      </button>

      {/* Screen reader announcement */}
      <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>
    </>
  );
}
```

### Keyboard Shortcut

```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Ctrl/Cmd + Shift + L: Toggle theme
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'l') {
      e.preventDefault();
      setTheme(theme === 'dark' ? 'light' : 'dark');
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [theme, setTheme]);
```

---

## Testing Dark Mode

### Manual Testing

1. Toggle between light/dark/system modes
2. Verify all text is readable (contrast ratios)
3. Check glassmorphism effects work in both modes
4. Ensure images/icons adapt appropriately
5. Test smooth transitions between themes

### Automated Testing

```typescript
import { render } from '@testing-library/react';
import { ThemeProvider } from 'next-themes';

test('Component renders correctly in dark mode', () => {
  const { container } = render(
    <ThemeProvider attribute="class" defaultTheme="dark">
      <TaskCard task={mockTask} />
    </ThemeProvider>
  );

  // Add .dark class to simulate dark mode
  document.documentElement.classList.add('dark');

  // Assertions...
});
```

---

## Performance Optimization

### Prevent Transition Flash

```css
/* Disable transitions temporarily when changing themes */
html.changing-theme *,
html.changing-theme *::before,
html.changing-theme *::after {
  transition: none !important;
}
```

```tsx
// Add/remove class when toggling
const handleToggle = () => {
  document.documentElement.classList.add('changing-theme');
  setTheme(newTheme);
  setTimeout(() => {
    document.documentElement.classList.remove('changing-theme');
  }, 100);
};
```

---

## Dark Mode Checklist

Before shipping:

- ✅ All text has sufficient contrast in both modes
- ✅ Glassmorphism effects work in dark mode
- ✅ Images/logos have dark mode variants (if needed)
- ✅ Shadows are visible in dark mode
- ✅ Focus indicators visible in both themes
- ✅ Theme toggle button accessible
- ✅ System preference respected by default
- ✅ Theme preference persists across sessions
- ✅ No FOUC on page load
- ✅ Smooth transitions between themes
- ✅ Screen reader announces theme changes

---

## Success Criteria

Dark mode implementation is complete when:

- ✅ Toggle between light, dark, and system themes
- ✅ System preference detected and applied automatically
- ✅ Theme preference saved to localStorage
- ✅ All components styled for both themes
- ✅ Color contrast meets WCAG AA in both modes
- ✅ Smooth transitions without flash
- ✅ Keyboard shortcut works (Ctrl+Shift+L)
- ✅ Screen reader announces theme changes
- ✅ No hydration errors in Next.js

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
