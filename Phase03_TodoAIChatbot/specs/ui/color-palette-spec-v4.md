# Color Palette Specification: Multi-User Full-Stack Todo Web Application (Tailwind CSS v4 Modern Approach)

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define comprehensive color palette for dark and light themes with modern Tailwind CSS v4 approach
**Version**: 2.0.0 (Tailwind CSS v4 Modern Approach)
**Last Updated**: 2026-01-05

---

## Dark Theme Color Palette

### Core Backgrounds
- **Background / App Root**: `#0B0A14`
- **Background Secondary**: `#121126`
- **Surface / Card**: `#181635`
- **Surface Elevated**: `#1E1B44`
- **Border / Divider**: `#2A275F`

### Primary & Secondary Accents
- **Primary Accent (Violet)**: `#8B5CF6`
- **Primary Hover**: `#7C3AED`
- **Primary Active**: `#6D28D9`
- **Accent Subtle BG**: `#221D4E`
- **Accent Glow (RGBA)**: `rgba(139,92,246,0.35)`

### Optional Secondary Accent (very subtle)
- **Secondary Accent (Indigo)**: `#6366F1`

### Text Colors
- **Text Primary**: `#EAEAF0`
- **Text Secondary**: `#C7C9E2`
- **Text Muted**: `#9AA0C7`
- **Text Disabled**: `#6B6F9C`

### Status / Semantic Colors
- **Success / Done**: `#4ADE80`
- **In Progress**: `#8B5CF6`
- **Pending**: `#A78BFA`
- **Warning / Overdue**: `#FBBF24`
- **Error / Failed**: `#FB7185`

### Interactive States
- **Hover BG**: `#211E4F`
- **Selected BG**: `#2A2563`
- **Focus Ring**: `#8B5CF6` (50% opacity)
- **Disabled BG**: `#14122C`

### Shadows & Glow
- **Card Shadow**: `0 8px 24px rgba(0,0,0,0.45)`
- **Accent Glow**: `0 0 20px rgba(139,92,246,0.35)`

---

## Light Theme Color Palette

### Core Backgrounds
- **Background / App Root**: `#FAFAFF`
- **Background Secondary**: `#F3F4FF`
- **Surface / Card**: `#FFFFFF`
- **Surface Elevated**: `#F8F9FF`
- **Border / Divider**: `#E2E5F5`

### Primary & Secondary Accents
- **Primary Accent (Violet)**: `#7C3AED`
- **Primary Hover**: `#6D28D9`
- **Primary Active**: `#5B21B6`
- **Accent Subtle BG**: `#EFEAFF`

### Optional Secondary Accent
- **Secondary Accent (Indigo)**: `#6366F1`

### Text Colors
- **Text Primary**: `#111827`
- **Text Secondary**: `#374151`
- **Text Muted**: `#6B7280`
- **Text Disabled**: `#9CA3AF`

### Status / Semantic Colors
- **Success / Done**: `#22C55E`
- **In Progress**: `#7C3AED`
- **Pending**: `#A78BFA`
- **Warning / Overdue**: `#F59E0B`
- **Error / Failed**: `#EF4444`

### Interactive States
- **Hover BG**: `#F1EDFF`
- **Selected BG**: `#E6DDFF`
- **Focus Ring**: `#7C3AED` (40% opacity)
- **Disabled BG**: `#F3F4F6`

### Shadows
- **Card Shadow**: `0 6px 18px rgba(124,58,237,0.12)`

---

## Modern Tailwind CSS v4 Configuration

### In app/globals.css (Modern Approach)

```css
@import "tailwindcss";

:root {
  /* Core Backgrounds - Light Theme */
  --color-bg-app-light: #FAFAFF;
  --color-bg-secondary-light: #F3F4FF;
  --color-surface-card-light: #FFFFFF;
  --color-surface-elevated-light: #F8F9FF;
  --color-border-divider-light: #E2E5F5;

  /* Primary Accents - Light Theme */
  --color-primary-accent-light: #7C3AED;
  --color-primary-hover-light: #6D28D9;
  --color-primary-active-light: #5B21B6;
  --color-accent-subtle-bg-light: #EFEAFF;

  /* Secondary Accent - Light Theme */
  --color-secondary-accent-light: #6366F1;

  /* Text Colors - Light Theme */
  --color-text-primary-light: #111827;
  --color-text-secondary-light: #374151;
  --color-text-muted-light: #6B7280;
  --color-text-disabled-light: #9CA3AF;

  /* Status Colors - Light Theme */
  --color-success-done-light: #22C55E;
  --color-in-progress-light: #7C3AED;
  --color-pending-light: #A78BFA;
  --color-warning-overdue-light: #F59E0B;
  --color-error-failed-light: #EF4444;

  /* Interactive States - Light Theme */
  --color-hover-bg-light: #F1EDFF;
  --color-selected-bg-light: #E6DDFF;
  --color-focus-ring-light: rgba(124, 58, 237, 0.4);
  --color-disabled-bg-light: #F3F4F6;

  /* Shadows - Light Theme */
  --shadow-card-light: 0 6px 18px rgba(124,58,237,0.12);

  /* Core Backgrounds - Dark Theme */
  --color-bg-app-dark: #0B0A14;
  --color-bg-secondary-dark: #121126;
  --color-surface-card-dark: #181635;
  --color-surface-elevated-dark: #1E1B44;
  --color-border-divider-dark: #2A275F;

  /* Primary Accents - Dark Theme */
  --color-primary-accent-dark: #8B5CF6;
  --color-primary-hover-dark: #7C3AED;
  --color-primary-active-dark: #6D28D9;
  --color-accent-subtle-bg-dark: #221D4E;
  --color-accent-glow-dark: rgba(139,92,246,0.35);

  /* Secondary Accent - Dark Theme */
  --color-secondary-accent-dark: #6366F1;

  /* Text Colors - Dark Theme */
  --color-text-primary-dark: #EAEAF0;
  --color-text-secondary-dark: #C7C9E2;
  --color-text-muted-dark: #9AA0C7;
  --color-text-disabled-dark: #6B6F9C;

  /* Status Colors - Dark Theme */
  --color-success-done-dark: #4ADE80;
  --color-in-progress-dark: #8B5CF6;
  --color-pending-dark: #A78BFA;
  --color-warning-overdue-dark: #FBBF24;
  --color-error-failed-dark: #FB7185;

  /* Interactive States - Dark Theme */
  --color-hover-bg-dark: #211E4F;
  --color-selected-bg-dark: #2A2563;
  --color-focus-ring-dark: rgba(139, 92, 246, 0.5);
  --color-disabled-bg-dark: #14122C;

  /* Shadows - Dark Theme */
  --shadow-card-dark: 0 8px 24px rgba(0,0,0,0.45);
  --shadow-accent-glow-dark: 0 0 20px rgba(139,92,246,0.35);
}

/* Dark mode variables */
.dark {
  --color-bg-app: var(--color-bg-app-dark);
  --color-bg-secondary: var(--color-bg-secondary-dark);
  --color-surface-card: var(--color-surface-card-dark);
  --color-surface-elevated: var(--color-surface-elevated-dark);
  --color-border-divider: var(--color-border-divider-dark);
  --color-primary-accent: var(--color-primary-accent-dark);
  --color-primary-hover: var(--color-primary-hover-dark);
  --color-primary-active: var(--color-primary-active-dark);
  --color-accent-subtle-bg: var(--color-accent-subtle-bg-dark);
  --color-accent-glow: var(--color-accent-glow-dark);
  --color-secondary-accent: var(--color-secondary-accent-dark);
  --color-text-primary: var(--color-text-primary-dark);
  --color-text-secondary: var(--color-text-secondary-dark);
  --color-text-muted: var(--color-text-muted-dark);
  --color-text-disabled: var(--color-text-disabled-dark);
  --color-success-done: var(--color-success-done-dark);
  --color-in-progress: var(--color-in-progress-dark);
  --color-pending: var(--color-pending-dark);
  --color-warning-overdue: var(--color-warning-overdue-dark);
  --color-error-failed: var(--color-error-failed-dark);
  --color-hover-bg: var(--color-hover-bg-dark);
  --color-selected-bg: var(--color-selected-bg-dark);
  --color-focus-ring: var(--color-focus-ring-dark);
  --color-disabled-bg: var(--color-disabled-bg-dark);
  --shadow-card: var(--shadow-card-dark);
  --shadow-accent-glow: var(--shadow-accent-glow-dark);
}

/* Light mode variables (default) */
:root {
  --color-bg-app: var(--color-bg-app-light);
  --color-bg-secondary: var(--color-bg-secondary-light);
  --color-surface-card: var(--color-surface-card-light);
  --color-surface-elevated: var(--color-surface-elevated-light);
  --color-border-divider: var(--color-border-divider-light);
  --color-primary-accent: var(--color-primary-accent-light);
  --color-primary-hover: var(--color-primary-hover-light);
  --color-primary-active: var(--color-primary-active-light);
  --color-accent-subtle-bg: var(--color-accent-subtle-bg-light);
  --color-secondary-accent: var(--color-secondary-accent-light);
  --color-text-primary: var(--color-text-primary-light);
  --color-text-secondary: var(--color-text-secondary-light);
  --color-text-muted: var(--color-text-muted-light);
  --color-text-disabled: var(--color-text-disabled-light);
  --color-success-done: var(--color-success-done-light);
  --color-in-progress: var(--color-in-progress-light);
  --color-pending: var(--color-pending-light);
  --color-warning-overdue: var(--color-warning-overdue-light);
  --color-error-failed: var(--color-error-failed-light);
  --color-hover-bg: var(--color-hover-bg-light);
  --color-selected-bg: var(--color-selected-bg-light);
  --color-focus-ring: var(--color-focus-ring-light);
  --color-disabled-bg: var(--color-disabled-bg-light);
  --shadow-card: var(--shadow-card-light);
}

/* Modern Tailwind CSS v4 theme configuration */
@theme {
  --color-bg-app: initial;
  --color-bg-secondary: initial;
  --color-surface-card: initial;
  --color-surface-elevated: initial;
  --color-border-divider: initial;
  --color-primary-accent: initial;
  --color-primary-hover: initial;
  --color-primary-active: initial;
  --color-accent-subtle-bg: initial;
  --color-accent-glow: initial;
  --color-secondary-accent: initial;
  --color-text-primary: initial;
  --color-text-secondary: initial;
  --color-text-muted: initial;
  --color-text-disabled: initial;
  --color-success-done: initial;
  --color-in-progress: initial;
  --color-pending: initial;
  --color-warning-overdue: initial;
  --color-error-failed: initial;
  --color-hover-bg: initial;
  --color-selected-bg: initial;
  --color-focus-ring: initial;
  --color-disabled-bg: initial;

  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --radius-2xl: calc(var(--radius) + 8px);
  --radius-3xl: calc(var(--radius) + 12px);
  --radius-4xl: calc(var(--radius) + 16px);

  --color-primary: var(--color-primary-accent);
  --color-primary-foreground: var(--color-text-primary);
  --color-secondary: var(--color-secondary-accent);
  --color-secondary-foreground: var(--color-text-primary);
  --color-accent: var(--color-accent-subtle-bg);
  --color-accent-foreground: var(--color-text-primary);
  --color-destructive: var(--color-error-failed);
  --color-destructive-foreground: var(--color-text-primary);
  --color-muted: var(--color-bg-secondary);
  --color-muted-foreground: var(--color-text-muted);
  --color-success: var(--color-success-done);
  --color-warning: var(--color-warning-overdue);
  --color-danger: var(--color-error-failed);
  --color-border: var(--color-border-divider);
  --color-input: var(--color-border-divider);
  --color-ring: var(--color-focus-ring);
  --color-background: var(--color-bg-app);
  --color-foreground: var(--color-text-primary);
  --color-card: var(--color-surface-card);
  --color-card-foreground: var(--color-text-primary);
  --color-popover: var(--color-surface-card);
  --color-popover-foreground: var(--color-text-primary);
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## Usage Guidelines

### Theme Switching
- Use `next-themes` for theme switching between dark and light modes
- All components should adapt to the current theme automatically through CSS variables
- Maintain consistent color relationships between themes

### Modern Tailwind CSS v4 Integration
- Define CSS variables in `:root` and `.dark` selectors in globals.css
- Use CSS variables with Tailwind's `dark:` variant for theme switching
- Apply font variables to html element in RootLayout (e.g., `className={`${inter.variable} ${jetbrains_mono.variable}`}`)
- Configure theme color in viewport metadata for browser chrome

### Accessibility Compliance
- All color combinations must meet WCAG 2.1 AA contrast requirements
- Primary text on background: 4.5:1 minimum contrast ratio
- Interactive elements: 3:1 minimum contrast ratio
- Test all color combinations with contrast checker tools

### Implementation Notes
- Store colors as CSS variables for easy theme switching
- Use Tailwind's dark: variant for conditional styling
- Ensure all UI elements respect the theme context
- Maintain consistent visual hierarchy across themes
- Apply font variables to html element in RootLayout for global font access

---

## Next.js Viewport Configuration

### In app/layout.tsx
For proper theme color handling in the browser chrome (address bar, task switcher), configure the viewport with theme color settings:

```typescript
import type { Viewport } from 'next'

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FAFAFF' },
    { media: '(prefers-color-scheme: dark)', color: '#0B0A14' },
  ],
  colorScheme: 'dark light',
}
```

This ensures the browser's UI adapts to match your application's theme, providing a more cohesive experience especially on mobile devices.

---

**Version**: 2.0.0 (Modern Tailwind CSS v4 Approach)
**Last Updated**: 2026-01-05
**Owner**: Phase 2 Development Team