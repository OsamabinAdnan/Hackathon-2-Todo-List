---
name: animation-integration
description: Add performant GSAP and Framer Motion animations to Next.js components with 60fps performance target. Use when (1) Adding micro-interactions like hover effects, entrance/exit transitions, stagger animations, (2) Implementing scroll-triggered animations with GSAP ScrollTrigger, (3) Creating complex animation timelines and sequences, (4) Adding smooth layout animations with Framer Motion's layout prop, (5) Implementing loading states with skeleton screens and spinners, (6) Enhancing user engagement with delightful motion design while respecting prefers-reduced-motion accessibility preference.
---

# Animation Integration

Add smooth, performant animations to Next.js components using GSAP and Framer Motion with 60fps performance target and accessibility support.

## Animation Library Selection

### When to Use Framer Motion
- Component-level animations (mount/unmount, layout shifts)
- Declarative React animations with JSX-friendly syntax
- Gestures (drag, hover, tap)
- Simple transitions and spring physics
- AnimatePresence for exit animations

### When to Use GSAP
- Complex animation timelines and sequences
- Scroll-triggered animations (ScrollTrigger)
- High-performance imperatives requiring precise control
- Chaining multiple animations with easing functions
- SVG morphing and advanced effects

## Core Animation Patterns

### 1. Micro-Interactions (Framer Motion)

**Hover Effects:**
```tsx
import { motion } from "framer-motion";

<motion.button
  whileHover={{ scale: 1.05, boxShadow: "0 10px 20px rgba(0,0,0,0.1)" }}
  whileTap={{ scale: 0.95 }}
  transition={{ duration: 0.2, ease: "easeOut" }}
>
  Click Me
</motion.button>
```

**Entrance/Exit Animations:**
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.95 }}
  transition={{ duration: 0.3 }}
>
  {content}
</motion.div>
```

### 2. Stagger Animations (Framer Motion)

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // 100ms delay between children
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.3, ease: [0, 0, 0.2, 1] },
  },
};

<motion.ul variants={containerVariants} initial="hidden" animate="visible">
  {tasks.map((task) => (
    <motion.li key={task.id} variants={itemVariants}>
      <TaskCard task={task} />
    </motion.li>
  ))}
</motion.ul>
```

### 3. Layout Animations (Framer Motion)

```tsx
<motion.div layout transition={{ duration: 0.3, ease: "easeInOut" }}>
  {/* Content that changes position smoothly */}
</motion.div>
```

### 4. Scroll-Triggered Animations (GSAP)

```tsx
'use client';

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function ScrollRevealSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    gsap.fromTo(
      sectionRef.current,
      { opacity: 0, y: 50 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 80%",
          end: "top 50%",
          toggleActions: "play none none reverse",
        },
      }
    );
  }, []);

  return <div ref={sectionRef}>{/* Content */}</div>;
}
```

### 5. Loading States

**Skeleton Screen:**
```tsx
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-neutral-200 dark:bg-zinc-700 rounded w-3/4"></div>
  <div className="h-4 bg-neutral-200 dark:bg-zinc-700 rounded"></div>
  <div className="h-4 bg-neutral-200 dark:bg-zinc-700 rounded w-5/6"></div>
</div>
```

**Spinner:**
```tsx
<motion.div
  className="h-8 w-8 border-4 border-neutral-200 border-t-primary-500 rounded-full"
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
/>
```

## Animation Standards from @specs/ui/animations.md

### Durations
- `instant`: 100ms (toggle switches, checkboxes)
- `fast`: 200ms (hover effects, button presses)
- `base`: 300ms (standard transitions, modals)
- `slow`: 500ms (complex layouts, page transitions)

### Easing Functions
- `easeOut`: Framer Motion `[0, 0, 0.2, 1]` / GSAP `"power2.out"` (default for most interactions)
- `easeInOut`: Framer Motion `[0.4, 0, 0.2, 1]` / GSAP `"power2.inOut"` (smooth two-way transitions)
- `bounce`: Framer Motion `{ type: "spring", stiffness: 300, damping: 20 }` (playful interactions)
- `smooth`: Framer Motion `[0.25, 0.1, 0.25, 1]` (glassmorphism effects)

### Performance Optimization
- Animate `transform` and `opacity` only (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left` (causes reflow)
- Use `will-change: transform` for complex animations
- Respect `prefers-reduced-motion` accessibility preference

## Accessibility: Reduced Motion Support

```tsx
'use client';

import { useEffect, useState } from "react";

export function useReducedMotion() {
  const [shouldReduceMotion, setShouldReduceMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setShouldReduceMotion(mediaQuery.matches);

    const handleChange = () => setShouldReduceMotion(mediaQuery.matches);
    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return shouldReduceMotion;
}

// Usage
export function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.3,
      }}
    >
      {content}
    </motion.div>
  );
}
```

## Complete Animation Examples

See `references/animation-patterns.md` for:
- TaskCard hover/entrance animations
- Modal entrance/exit with backdrop fade
- Page transitions (fade, slide)
- Ripple effect on button click
- Toast notification slide-in from top
- Complex GSAP timelines
- Scroll-based parallax effects

## Quality Checklist

- [ ] Animation runs at 60fps (check with browser DevTools)
- [ ] Uses `transform` and `opacity` for performance
- [ ] Respects `prefers-reduced-motion` accessibility setting
- [ ] Duration follows standards (100ms-500ms range)
- [ ] Easing function chosen appropriately for interaction type
- [ ] Exit animations implemented for modals/toasts
- [ ] No animation jank or stuttering
- [ ] Animations enhance UX without distracting

## References

- **Animation Standards**: `@specs/ui/animations.md` for duration/easing specifications
- **Complete Examples**: `references/animation-patterns.md` for production-ready patterns
- **Performance**: Target 60fps, use GPU-accelerated properties only
