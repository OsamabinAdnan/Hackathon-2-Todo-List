---
name: theme-palette-application
description: Apply color palettes, glassmorphism effects, and dark mode implementation using Tailwind CSS and next-themes. Use when (1) Configuring tailwind.config.ts with design tokens (colors, typography, spacing), (2) Implementing dark mode with next-themes provider and class strategy, (3) Applying glassmorphism effects with backdrop-blur and opacity layers, (4) Creating theme toggle components with smooth transitions, (5) Ensuring consistent branding across pages like login/signup and dashboard, (6) Setting up CSS variables for light/dark color schemes with proper contrast ratios.
---

# Theme & Palette Application

Apply modern aesthetic color palettes with Tailwind CSS, implement dark mode with next-themes, and create glassmorphism effects for premium UI.

## Core Capabilities

### 1. Tailwind Config Setup

Configure `tailwind.config.ts` with design tokens from `@specs/ui/design-system.md`:

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class', // Enable dark mode with class strategy
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary color palette
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa', // Dark mode primary (lighter for contrast)
          500: '#3b82f6', // Light mode primary
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        // Neutral palette
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        // Semantic colors
        success: { DEFAULT: '#10b981', dark: '#34d399' },
        warning: { DEFAULT: '#f59e0b', dark: '#fbbf24' },
        error: { DEFAULT: '#ef4444', dark: '#f87171' },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'monospace'],
      },
      spacing: {
        // 8px base unit (already included in default Tailwind, but documenting)
        // 0.5 = 2px, 1 = 4px, 2 = 8px, 3 = 12px, 4 = 16px, etc.
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};

export default config;
```

### 2. Dark Mode Implementation

**Install next-themes:**
```bash
npm install next-themes
```

**Root Layout Setup:**
```tsx
// app/layout.tsx
import { ThemeProvider } from 'next-themes';
import { Inter, JetBrains_Mono } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains-mono' });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrainsMono.variable}`}>
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

**Global CSS Variables:**
```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light mode colors */
    --background: 250 250 250; /* #fafafa */
    --foreground: 23 23 23; /* #171717 */
    --primary: 59 130 246; /* #3b82f6 */
    --glass-bg: rgba(255, 255, 255, 0.1);
    --glass-border: rgba(255, 255, 255, 0.2);
  }

  .dark {
    /* Dark mode colors */
    --background: 24 24 27; /* #18181b */
    --foreground: 250 250 250; /* #fafafa */
    --primary: 96 165 250; /* #60a5fa - lighter for contrast */
    --glass-bg: rgba(0, 0, 0, 0.3);
    --glass-border: rgba(255, 255, 255, 0.1);
  }
}

/* Smooth color transitions */
* {
  transition: background-color 200ms ease, border-color 200ms ease, color 200ms ease;
}
```

### 3. Theme Toggle Component

```tsx
'use client';

import { useTheme } from 'next-themes';
import { MoonIcon, SunIcon } from 'lucide-react';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-10 w-10 rounded-md bg-neutral-100 dark:bg-neutral-800" />;
  }

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="relative h-10 w-10 rounded-md bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 transition-colors duration-200 flex items-center justify-center"
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

### 4. Glassmorphism Effects

**Standard Glass Card:**
```tsx
<div className="bg-white/10 dark:bg-black/30 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-lg p-6">
  {/* Content */}
</div>
```

**Glass Variants:**
```tsx
// Subtle (5% opacity, 8px blur)
<div className="bg-white/5 dark:bg-black/20 backdrop-blur-[8px] border border-white/10">

// Standard (10% opacity, 12px blur)
<div className="bg-white/10 dark:bg-black/30 backdrop-blur-md border border-white/20 dark:border-white/10">

// Strong (70% opacity, 20px blur)
<div className="bg-white/70 dark:bg-black/60 backdrop-blur-xl border border-white/30 dark:border-white/20">
```

**Gradient Backgrounds for Glass Effects:**
```tsx
<div className="min-h-screen bg-linear-to-br from-neutral-50 via-neutral-100 to-neutral-200 dark:from-zinc-900 dark:via-zinc-950 dark:to-black">
  {/* Glass components look best on gradient backgrounds */}
</div>
```

### 5. Color Application Patterns

**Backgrounds:**
```tsx
<div className="bg-white dark:bg-zinc-900">                    {/* Page background */}
<div className="bg-neutral-50 dark:bg-zinc-800">              {/* Card background */}
<div className="bg-neutral-100 dark:bg-zinc-700">             {/* Hover state */}
```

**Text:**
```tsx
<h1 className="text-neutral-900 dark:text-neutral-50">        {/* Primary text */}
<p className="text-neutral-600 dark:text-neutral-400">        {/* Secondary text */}
<span className="text-neutral-500 dark:text-neutral-500">    {/* Disabled text */}
```

**Borders:**
```tsx
<div className="border border-neutral-200 dark:border-zinc-700">
<div className="border-b border-neutral-200 dark:border-zinc-700">  {/* Divider */}
```

**Buttons:**
```tsx
<button className="bg-primary-500 hover:bg-primary-600 text-white dark:bg-primary-400 dark:hover:bg-primary-500">
  Primary Button
</button>

<button className="bg-red-500 hover:bg-red-600 text-white">
  Destructive Button
</button>
```

### 6. Consistent Branding Example

**Login/Signup Pages:**
```tsx
export default function LoginPage() {
  return (
    <div className="min-h-screen bg-linear-to-br from-primary-50 via-white to-neutral-50 dark:from-zinc-900 dark:via-zinc-950 dark:to-black flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white/70 dark:bg-black/40 backdrop-blur-xl border border-white/30 dark:border-white/10 rounded-2xl p-8 shadow-2xl">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-50 mb-2">
          Welcome Back
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8">
          Sign in to your account
        </p>
        {/* Login form */}
      </div>
    </div>
  );
}
```

**Dashboard:**
```tsx
<div className="min-h-screen bg-linear-to-br from-neutral-50 to-neutral-100 dark:from-zinc-900 dark:to-zinc-950">
  <Sidebar className="bg-white/80 dark:bg-zinc-900/90 backdrop-blur-md border-r border-neutral-200 dark:border-zinc-700" />
  <Header className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border-b border-neutral-200 dark:border-zinc-700" />
  <main>{/* Content */}</main>
</div>
```

## Quality Checklist

- [ ] Tailwind config includes all design tokens from `@specs/ui/design-system.md`
- [ ] Dark mode enabled with `darkMode: 'class'`
- [ ] next-themes provider configured in root layout
- [ ] All color utilities include `dark:` variants
- [ ] Glassmorphism effects use `backdrop-blur` and proper opacity
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] Theme toggle component prevents hydration errors
- [ ] Smooth transitions configured (200ms duration)
- [ ] Consistent branding across all pages
- [ ] System preference detected by default

## References

- **Design System**: `@specs/ui/design-system.md` for complete color palette and design tokens
- **Dark Mode Spec**: `@specs/ui/dark-mode.md` for next-themes implementation details
- **Glassmorphism**: `@specs/ui/glassmorphism.md` for glass effect patterns and variants
- **Color Palette Reference**: `references/color-palette.md` for complete hex codes and usage examples
