# Animation Specification

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define all animations using GSAP and Framer Motion for delightful micro-interactions
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Animation Philosophy

Create **smooth, delightful micro-interactions** that:

- **Enhance usability**: Guide user attention and provide feedback
- **Feel natural**: Match real-world physics (easing, momentum)
- **Perform well**: Target 60fps on all devices
- **Stay subtle**: Don't distract from primary tasks

**Performance Target**: All animations must run at 60fps (16.67ms per frame)

---

## Animation Libraries

### GSAP (GreenSock Animation Platform)

**Use For:**
- Complex timeline animations
- Page transitions
- Scroll-triggered animations
- Stagger effects
- SVG animations

**Installation:**
```bash
npm install gsap
```

**Why GSAP:**
- Industry-leading performance
- Powerful timeline control
- Works with any property
- Backward compatible with older browsers

---

### Framer Motion

**Use For:**
- React component animations
- Layout animations (position changes)
- Gesture-based animations (drag, tap)
- Variants for consistent animation sets
- Exit animations

**Installation:**
```bash
npm install framer-motion
```

**Why Framer Motion:**
- React-first API
- Declarative syntax
- Built-in layout animations
- Excellent TypeScript support

---

## Easing Functions

### Standard Easings

```typescript
// Framer Motion
const easings = {
  easeInOut: [0.4, 0, 0.2, 1],       // Default smooth
  easeOut: [0, 0, 0.2, 1],           // Exits (elements leaving)
  easeIn: [0.4, 0, 1, 1],            // Entrances (elements appearing)
  bounce: [0.68, -0.55, 0.265, 1.55], // Playful bounce
  smooth: [0.25, 0.1, 0.25, 1],      // Ultra smooth
};

// GSAP
gsap.to(element, {
  x: 100,
  ease: "power2.out",      // Equivalent to easeOut
  ease: "power2.inOut",    // Equivalent to easeInOut
  ease: "back.out(1.7)",   // Bounce effect
  ease: "elastic.out(1, 0.5)", // Elastic bounce
});
```

### Custom Cubic Bezier

```typescript
// Framer Motion
const customEasing = [0.22, 1, 0.36, 1]; // Fast start, slow end

// GSAP
gsap.to(element, {
  x: 100,
  ease: "cubic-bezier(0.22, 1, 0.36, 1)",
});
```

---

## Duration Standards

```typescript
export const durations = {
  instant: 100,   // Hover states, tooltips
  fast: 200,      // Button clicks, simple transitions
  base: 300,      // Default for most animations
  slow: 500,      // Page transitions, complex animations
  slower: 700,    // Modal entrances, major state changes
};
```

---

## Common Animations

### 1. Fade In/Out

**Framer Motion:**
```tsx
import { motion } from "framer-motion";

export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

**GSAP:**
```typescript
import gsap from "gsap";

gsap.from(".task-card", {
  opacity: 0,
  duration: 0.3,
  ease: "power2.out",
});
```

---

### 2. Slide In (from bottom)

**Framer Motion:**
```tsx
<motion.div
  initial={{ y: 20, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  exit={{ y: -20, opacity: 0 }}
  transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
>
  {children}
</motion.div>
```

**GSAP:**
```typescript
gsap.from(".notification", {
  y: 20,
  opacity: 0,
  duration: 0.3,
  ease: "power2.out",
});
```

---

### 3. Scale In (Zoom)

**Framer Motion:**
```tsx
<motion.div
  initial={{ scale: 0.95, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  exit={{ scale: 0.95, opacity: 0 }}
  transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
>
  {children}
</motion.div>
```

**GSAP:**
```typescript
gsap.from(".modal", {
  scale: 0.95,
  opacity: 0,
  duration: 0.2,
  ease: "power2.out",
});
```

---

### 4. Stagger Animation (List Items)

**Framer Motion:**
```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // 100ms delay between each child
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

export function TaskList({ tasks }: TaskListProps) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {tasks.map(task => (
        <motion.li key={task.id} variants={itemVariants}>
          <TaskCard task={task} />
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

**GSAP:**
```typescript
gsap.from(".task-card", {
  y: 20,
  opacity: 0,
  duration: 0.3,
  stagger: 0.1, // 100ms delay between each
  ease: "power2.out",
});
```

---

### 5. Hover Scale Effect

**Framer Motion:**
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click Me
</motion.button>
```

**CSS (for simple hovers):**
```css
.button {
  transition: transform 200ms cubic-bezier(0, 0, 0.2, 1);
}

.button:hover {
  transform: scale(1.05);
}

.button:active {
  transform: scale(0.95);
}
```

---

### 6. Layout Animation (Position Changes)

**Framer Motion:**
```tsx
<motion.div layout transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}>
  {/* Content that changes position */}
</motion.div>
```

**Use Case**: Task cards reordering after filtering/sorting

```tsx
export function TaskCard({ task }: TaskCardProps) {
  return (
    <motion.div
      layout // Automatically animates position changes
      layoutId={task.id} // Maintains identity across renders
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="glass-card p-6"
    >
      <h3>{task.title}</h3>
    </motion.div>
  );
}
```

---

### 7. Exit Animations

**Framer Motion with AnimatePresence:**
```tsx
import { AnimatePresence } from "framer-motion";

export function TaskList({ tasks }: TaskListProps) {
  return (
    <AnimatePresence>
      {tasks.map(task => (
        <motion.div
          key={task.id}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0, transition: { duration: 0.2 } }}
        >
          <TaskCard task={task} />
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
```

---

## Component-Specific Animations

### Task Card Hover

```tsx
export function TaskCard({ task }: TaskCardProps) {
  return (
    <motion.div
      className="glass-card p-6 cursor-pointer"
      whileHover={{
        scale: 1.02,
        boxShadow: "0 12px 48px rgba(31, 38, 135, 0.2)",
        transition: { duration: 0.2 },
      }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Task content */}
    </motion.div>
  );
}
```

### Modal Entrance

```tsx
export function Modal({ isOpen, onClose, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay fade in */}
          <motion.div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
          />

          {/* Modal scale + fade in */}
          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
          >
            <div className="glass-strong rounded-xl p-6 max-w-lg w-full">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### Button Ripple Effect

```tsx
import { useState } from "react";

export function RippleButton({ children, onClick }: ButtonProps) {
  const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setRipples([...ripples, { x, y, id: Date.now() }]);
    setTimeout(() => setRipples(r => r.slice(1)), 600);

    onClick?.(e);
  };

  return (
    <button
      onClick={handleClick}
      className="relative overflow-hidden btn-primary"
    >
      {children}

      {ripples.map(ripple => (
        <motion.span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 0,
            height: 0,
          }}
          animate={{
            width: 300,
            height: 300,
            x: -150,
            y: -150,
            opacity: [0.5, 0],
          }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      ))}
    </button>
  );
}
```

### Notification Toast Slide In

```tsx
export function Toast({ message, type }: ToastProps) {
  return (
    <motion.div
      className={`
        glass-standard p-4 rounded-lg shadow-xl
        ${type === 'success' ? 'border-l-4 border-success-500' : ''}
        ${type === 'error' ? 'border-l-4 border-danger-500' : ''}
      `}
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
    >
      <p className="font-medium">{message}</p>
    </motion.div>
  );
}
```

---

## Page Transitions

### Simple Fade Transition

```tsx
// app/layout.tsx
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <html>
      <body>
        <AnimatePresence mode="wait">
          <motion.div
            key={pathname}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </body>
    </html>
  );
}
```

### Slide Transition

```tsx
<motion.div
  key={pathname}
  initial={{ x: 20, opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  exit={{ x: -20, opacity: 0 }}
  transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
>
  {children}
</motion.div>
```

---

## Scroll Animations (GSAP ScrollTrigger)

### Fade In On Scroll

```typescript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

useEffect(() => {
  gsap.from(".stat-card", {
    opacity: 0,
    y: 50,
    duration: 0.6,
    stagger: 0.2,
    scrollTrigger: {
      trigger: ".stats-section",
      start: "top 80%", // When top of .stats-section reaches 80% of viewport
      end: "bottom 20%",
      toggleActions: "play none none none",
    },
  });
}, []);
```

### Parallax Effect

```typescript
gsap.to(".hero-background", {
  y: 100,
  scrollTrigger: {
    trigger: ".hero",
    start: "top top",
    end: "bottom top",
    scrub: true, // Smooth scrubbing
  },
});
```

---

## Loading Animations

### Spinner

```tsx
export function Spinner() {
  return (
    <motion.div
      className="h-8 w-8 border-4 border-primary-200 border-t-primary-600 rounded-full"
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    />
  );
}
```

### Skeleton Loader with Pulse

```tsx
export function SkeletonCard() {
  return (
    <motion.div
      className="glass-card p-6"
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
    >
      <div className="h-6 bg-neutral-300 rounded w-1/3 mb-4" />
      <div className="space-y-2">
        <div className="h-4 bg-neutral-300 rounded w-full" />
        <div className="h-4 bg-neutral-300 rounded w-5/6" />
      </div>
    </motion.div>
  );
}
```

---

## Performance Best Practices

### DO: Animate Transform & Opacity (GPU Accelerated)

```tsx
<motion.div
  animate={{ x: 100, opacity: 1 }} // ✅ Fast (GPU)
/>
```

### DON'T: Animate Width/Height/Top/Left

```tsx
<motion.div
  animate={{ width: 200, top: 50 }} // ❌ Slow (causes reflow)
/>
```

### Force GPU Acceleration

```css
.animated-element {
  transform: translateZ(0); /* Force GPU layer */
  will-change: transform, opacity; /* Hint to browser */
}
```

### Reduce Animations on Low-End Devices

```typescript
import { useReducedMotion } from "framer-motion";

export function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={shouldReduceMotion ? {} : { x: 100, opacity: 1 }}
    />
  );
}
```

---

## Accessibility

### Respect User Preferences

```typescript
// Detect if user prefers reduced motion
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (!prefersReducedMotion) {
  // Apply animations
}
```

### Focus Indicators with Animation

```tsx
<motion.button
  className="btn-primary"
  whileFocus={{ scale: 1.05, boxShadow: "0 0 0 4px rgba(59, 130, 246, 0.3)" }}
  transition={{ duration: 0.15 }}
>
  Click Me
</motion.button>
```

---

## Success Criteria

Animation implementation is complete when:

- ✅ All animations run at 60fps (no jank)
- ✅ Micro-interactions feel responsive (< 200ms)
- ✅ Page transitions are smooth and consistent
- ✅ Stagger animations work for lists
- ✅ Exit animations complete before unmounting
- ✅ Loading states have animations
- ✅ Hover effects enhance interactivity
- ✅ Reduced motion preference is respected
- ✅ GPU-accelerated properties used (transform, opacity)
- ✅ No layout shift during animations

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
