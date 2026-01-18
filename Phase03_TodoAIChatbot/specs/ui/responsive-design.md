# Responsive Design Specification

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define responsive design patterns for mobile, tablet, and desktop experiences
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Responsive Design Philosophy

Build with **mobile-first approach**:

- **Start with mobile**: Design for smallest screen first, then enhance
- **Progressive enhancement**: Add complexity as screen size increases
- **Content parity**: All features accessible on all devices
- **Touch-friendly**: 44×44px minimum touch targets
- **Adaptive layouts**: Graceful transitions between breakpoints

---

## Breakpoints

### Standard Breakpoints (Tailwind defaults)

```typescript
export const breakpoints = {
  sm: 640,    // Small tablets (portrait)
  md: 768,    // Tablets (portrait) and large phones (landscape)
  lg: 1024,   // Small laptops and tablets (landscape)
  xl: 1280,   // Desktops
  '2xl': 1536, // Large desktops
};
```

### Media Queries

```css
/* Mobile first approach */
.container {
  padding: 1rem; /* Mobile: 16px */
}

@media (min-width: 640px) {  /* Small tablets */
  .container {
    padding: 1.5rem; /* 24px */
  }
}

@media (min-width: 768px) {  /* Tablets */
  .container {
    padding: 2rem; /* 32px */
  }
}

@media (min-width: 1024px) { /* Laptops */
  .container {
    padding: 3rem; /* 48px */
  }
}
```

### Tailwind Responsive Classes

```tsx
<div className="
  p-4 sm:p-6 md:p-8 lg:p-12
  text-sm sm:text-base md:text-lg
  grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3
">
```

---

## Mobile Layout (< 768px)

### Screen Dimensions
- **Minimum width**: 320px (iPhone SE)
- **Common widths**: 375px (iPhone), 390px (iPhone Pro), 428px (iPhone Pro Max)
- **Viewport height**: Variable (avoid fixed heights)

### Layout Structure

```
┌───────────────────────┐
│  Header (56px)        │
│  [☰] Logo    [🔍][+]  │
├───────────────────────┤
│                       │
│  Content (full-width) │
│  Padding: 16px        │
│                       │
│  ┌─────────────────┐ │
│  │  Card (stack)   │ │
│  ├─────────────────┤ │
│  │  Card           │ │
│  ├─────────────────┤ │
│  │  Card           │ │
│  └─────────────────┘ │
│                       │
├───────────────────────┤
│  Bottom Nav (56px)    │
│  [Home][Tasks][+][·]  │
└───────────────────────┘
```

### Mobile-Specific Patterns

#### 1. Hamburger Menu

```tsx
export function MobileHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 h-14 bg-white/80 backdrop-blur-md border-b z-20 px-4">
        <div className="flex items-center justify-between h-full">
          {/* Hamburger */}
          <button
            onClick={() => setIsMenuOpen(true)}
            className="p-2 -ml-2"
            aria-label="Open menu"
          >
            <MenuIcon className="h-6 w-6" />
          </button>

          {/* Logo */}
          <span className="font-mono font-bold">TaskFlow</span>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            <button className="p-2" aria-label="Search">
              <SearchIcon className="h-5 w-5" />
            </button>
            <button className="p-2" aria-label="Add task">
              <PlusIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Off-canvas menu */}
      <MobileMenu isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
    </>
  );
}
```

#### 2. Off-Canvas Drawer

```tsx
import { motion, AnimatePresence } from "framer-motion";

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.nav
            className="fixed top-0 left-0 bottom-0 w-80 max-w-[85vw] bg-white shadow-2xl z-40 p-6"
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 20 }}
          >
            {/* Navigation items */}
            <NavItem icon={HomeIcon} label="Dashboard" href="/dashboard" />
            <NavItem icon={ListIcon} label="All Tasks" href="/tasks" />
            {/* ... more items */}
          </motion.nav>
        </>
      )}
    </AnimatePresence>
  );
}
```

#### 3. Bottom Navigation

```tsx
export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-14 bg-white border-t border-neutral-200 safe-area-inset-bottom">
      <div className="flex justify-around items-center h-full">
        <NavButton
          icon={HomeIcon}
          label="Home"
          href="/dashboard"
          active={pathname === "/dashboard"}
        />
        <NavButton
          icon={ListIcon}
          label="Tasks"
          href="/tasks"
          active={pathname === "/tasks"}
        />

        {/* Floating Action Button */}
        <button
          className="
            h-12 w-12 rounded-full
            bg-primary-500 text-white
            shadow-xl -mt-6
            flex items-center justify-center
          "
          aria-label="New task"
        >
          <PlusIcon className="h-6 w-6" />
        </button>

        <NavButton icon={CalendarIcon} label="Calendar" href="/calendar" />
        <NavButton icon={MoreIcon} label="More" href="/settings" />
      </div>
    </nav>
  );
}
```

#### 4. Swipe Gestures

```tsx
import { motion, PanInfo } from "framer-motion";

export function SwipeableCard({ task, onDelete }: SwipeableCardProps) {
  const handleDragEnd = (event: any, info: PanInfo) => {
    if (info.offset.x < -100) {
      // Swiped left to delete
      onDelete(task.id);
    }
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -120, right: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      className="relative"
    >
      <div className="glass-card p-4">
        <h3>{task.title}</h3>
      </div>

      {/* Delete button (revealed on swipe) */}
      <div className="absolute right-0 top-0 bottom-0 w-20 bg-danger-500 flex items-center justify-center rounded-r-lg">
        <TrashIcon className="h-6 w-6 text-white" />
      </div>
    </motion.div>
  );
}
```

#### 5. Touch-Friendly Sizing

```tsx
{/* Minimum touch target: 44×44px */}
<button className="h-11 w-11 flex items-center justify-center">
  <Icon className="h-6 w-6" />
</button>

{/* Input fields: larger on mobile */}
<input className="h-12 px-4 text-base" />

{/* Checkbox/radio: larger on mobile */}
<input type="checkbox" className="h-6 w-6" />
```

---

## Tablet Layout (768px - 1023px)

### Layout Structure

```
┌─────────────────────────────────────┐
│  Header (64px)                      │
│  [Logo]     [Search]    [User]      │
├──────┬──────────────────────────────┤
│ Icon │  Content Area                │
│ Side │                              │
│ bar  │  ┌────────┬────────┐        │
│      │  │  Card  │  Card  │        │
│ (64) │  ├────────┼────────┤        │
│      │  │  Card  │  Card  │        │
│      │  └────────┴────────┘        │
│      │                              │
└──────┴──────────────────────────────┘
```

### Tablet-Specific Changes

1. **Sidebar**: Icon-only (64px width)
2. **Grid**: 2 columns for cards
3. **Typography**: Slightly larger than mobile
4. **Touch targets**: Maintain 44×44px minimum

```tsx
{/* Tablet: 2 columns */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  {tasks.map(task => <TaskCard key={task.id} task={task} />)}
</div>
```

---

## Desktop Layout (1024px+)

### Layout Structure

```
┌──────────────────────────────────────────────┐
│  Header (64px)                               │
│  [Logo]     [Search Bar]       [User Menu]   │
├──────────┬───────────────────────────────────┤
│          │                                   │
│ Sidebar  │  Content Area (max-width)        │
│ (240px)  │                                   │
│          │  ┌───────┬───────┬───────┐      │
│ [Nav]    │  │ Card  │ Card  │ Card  │      │
│ [Nav]    │  ├───────┼───────┼───────┤      │
│ [Nav]    │  │ Card  │ Card  │ Card  │      │
│          │  └───────┴───────┴───────┘      │
│          │                                   │
└──────────┴───────────────────────────────────┘
```

### Desktop-Specific Features

1. **Full sidebar**: 240px with labels
2. **Grid**: 3-4 columns for cards
3. **Search bar**: Always visible in header
4. **Hover states**: More prominent
5. **Keyboard shortcuts**: Visible hints

```tsx
{/* Desktop: 3 columns */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {tasks.map(task => <TaskCard key={task.id} task={task} />)}
</div>
```

---

## Responsive Components

### Responsive Images

```tsx
import Image from "next/image";

export function ResponsiveImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Dashboard"
      width={1920}
      height={1080}
      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
      priority
    />
  );
}
```

### Responsive Typography

```tsx
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
  Welcome to TaskFlow
</h1>

<p className="text-sm sm:text-base md:text-lg text-neutral-600">
  Manage your tasks efficiently
</p>
```

### Responsive Spacing

```tsx
<div className="
  p-4 sm:p-6 md:p-8 lg:p-12
  space-y-4 sm:space-y-6 md:space-y-8
">
```

### Responsive Grid

```tsx
{/* Mobile: 1 col, Tablet: 2 cols, Desktop: 3 cols, Large: 4 cols */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
```

---

## Container Widths

### Max-Width Containers

```tsx
{/* Full width on mobile, constrained on desktop */}
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  {/* Max-width: 1280px (xl) */}
</div>

{/* Custom max-widths */}
<div className="max-w-7xl mx-auto px-4">
  {/* Max-width: 1280px */}
</div>

<div className="max-w-4xl mx-auto px-4">
  {/* Max-width: 896px (for reading content) */}
</div>
```

---

## Responsive Utilities

### Show/Hide Based on Screen Size

```tsx
{/* Show on mobile only */}
<div className="block md:hidden">
  <MobileMenu />
</div>

{/* Show on desktop only */}
<div className="hidden md:block">
  <DesktopSidebar />
</div>

{/* Show on tablet and above */}
<div className="hidden sm:block">
  <SearchBar />
</div>
```

### Conditional Rendering (React)

```tsx
import { useMediaQuery } from "@/hooks/useMediaQuery";

export function ResponsiveComponent() {
  const isMobile = useMediaQuery("(max-width: 768px)");

  return isMobile ? <MobileView /> : <DesktopView />;
}
```

**useMediaQuery Hook:**
```typescript
import { useState, useEffect } from "react";

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = () => setMatches(media.matches);
    media.addEventListener("change", listener);

    return () => media.removeEventListener("change", listener);
  }, [query]);

  return matches;
}
```

---

## Forms on Mobile

### Stacked Inputs

```tsx
{/* Mobile: Stack vertically, Desktop: Side by side */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <input
    type="text"
    placeholder="First Name"
    className="input"
  />
  <input
    type="text"
    placeholder="Last Name"
    className="input"
  />
</div>
```

### Mobile-Optimized Input Types

```tsx
{/* Use correct input types for mobile keyboards */}
<input type="email" inputMode="email" />  {/* Email keyboard */}
<input type="tel" inputMode="tel" />      {/* Phone keyboard */}
<input type="number" inputMode="numeric" /> {/* Number keyboard */}
<input type="url" inputMode="url" />      {/* URL keyboard */}
```

---

## Testing Responsive Design

### Browser DevTools

1. Open Chrome DevTools (F12)
2. Click device toolbar (Ctrl+Shift+M)
3. Test common devices:
   - iPhone SE (375×667)
   - iPhone 12 Pro (390×844)
   - iPad (768×1024)
   - iPad Pro (1024×1366)
   - Desktop (1920×1080)

### Manual Testing

- **Real devices**: Test on actual phones/tablets
- **Orientation**: Test portrait and landscape
- **Font size**: Test with larger system fonts
- **Network**: Test on slower connections

### Responsive Design Checklist

- ✅ All content accessible on mobile
- ✅ Touch targets ≥ 44×44px
- ✅ Text readable without zooming (min 16px)
- ✅ No horizontal scrolling
- ✅ Images scale appropriately
- ✅ Forms easy to fill on mobile
- ✅ Navigation intuitive on all devices
- ✅ Performance fast on mobile (< 3s load)

---

## Safe Area Insets (iPhone notch/home indicator)

```css
/* Account for iPhone notch and home indicator */
.header {
  padding-top: env(safe-area-inset-top);
}

.bottom-nav {
  padding-bottom: env(safe-area-inset-bottom);
}
```

```tsx
<nav className="
  fixed bottom-0 left-0 right-0
  pb-safe-area-bottom
  bg-white
">
```

---

## Success Criteria

Responsive design is complete when:

- ✅ App works on screens from 320px to 1920px+
- ✅ Touch targets are minimum 44×44px on mobile
- ✅ Typography scales appropriately across breakpoints
- ✅ Layouts adapt gracefully (no broken designs)
- ✅ Images are optimized for each screen size
- ✅ Navigation is intuitive on all devices
- ✅ Performance is fast on mobile networks
- ✅ Safe area insets respected on iOS devices
- ✅ Orientation changes handled smoothly
- ✅ Content parity across all devices

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
