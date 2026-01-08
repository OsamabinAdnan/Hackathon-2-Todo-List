# Glassmorphism Design Patterns Specification

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define glassmorphism visual effects for depth, elegance, and modern aesthetic
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## What is Glassmorphism?

Glassmorphism is a design trend featuring:
- **Frosted glass effect**: Semi-transparent backgrounds with blur
- **Layered depth**: Visual hierarchy through transparency and shadows
- **Subtle borders**: Light borders that enhance the glass effect
- **Vibrant backgrounds**: Colorful gradients behind glass elements

**Why Glassmorphism for Todo App:**
- Creates premium, modern aesthetic
- Adds visual depth without clutter
- Makes UI feel lightweight and elegant
- Stands out from flat Material Design competitors

---

## Core Glassmorphism Properties

### 1. Background Opacity

**Light Mode:**
```css
background: rgba(255, 255, 255, 0.1);  /* Subtle - 10% white */
background: rgba(255, 255, 255, 0.3);  /* Medium - 30% white */
background: rgba(255, 255, 255, 0.7);  /* Strong - 70% white (modals) */
```

**Dark Mode:**
```css
background: rgba(0, 0, 0, 0.2);   /* Subtle - 20% black */
background: rgba(0, 0, 0, 0.4);   /* Medium - 40% black */
background: rgba(0, 0, 0, 0.7);   /* Strong - 70% black (modals) */
```

### 2. Backdrop Blur

```css
backdrop-filter: blur(8px);   /* Subtle - slight frosting */
backdrop-filter: blur(12px);  /* Standard - clear frosting */
backdrop-filter: blur(20px);  /* Strong - heavy frosting (modals) */
backdrop-filter: blur(24px);  /* Extra strong - maximum frosting */

/* With saturation boost for vibrancy */
backdrop-filter: blur(12px) saturate(180%);
```

### 3. Border Styling

```css
border: 1px solid rgba(255, 255, 255, 0.1);  /* Subtle edge */
border: 1px solid rgba(255, 255, 255, 0.2);  /* Standard edge */
border: 1px solid rgba(255, 255, 255, 0.3);  /* Strong edge */
```

### 4. Shadow Layering

```css
box-shadow:
  0 8px 32px 0 rgba(31, 38, 135, 0.15),     /* Outer shadow */
  0 4px 16px 0 rgba(31, 38, 135, 0.08);     /* Inner shadow */
```

---

## Glass Component Variants

### Variant 1: Subtle Glass (Sidebar, Background Cards)

**Use Case**: Background elements that shouldn't dominate

```tsx
<div className="
  bg-white/5 backdrop-blur-[8px]
  border border-white/10
  rounded-lg
  shadow-sm
">
  {/* Minimal glass effect */}
</div>
```

**CSS:**
```css
.glass-subtle {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px) saturate(120%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
```

---

### Variant 2: Standard Glass (Task Cards, Panels)

**Use Case**: Primary content cards

```tsx
<div className="
  bg-white/10 backdrop-blur-md
  border border-white/20
  rounded-lg
  shadow-lg
  hover:shadow-xl
  transition-shadow duration-300
">
  {/* Standard glass effect */}
</div>
```

**CSS:**
```css
.glass-standard {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.15),
    0 4px 16px 0 rgba(31, 38, 135, 0.08);
  transition: box-shadow 0.3s ease;
}

.glass-standard:hover {
  box-shadow:
    0 12px 48px 0 rgba(31, 38, 135, 0.2),
    0 6px 24px 0 rgba(31, 38, 135, 0.12);
}
```

---

### Variant 3: Strong Glass (Modals, Dropdowns)

**Use Case**: Overlays that need to be clearly separated

```tsx
<div className="
  bg-white/70 backdrop-blur-xl
  border border-white/30
  rounded-xl
  shadow-2xl
">
  {/* Strong glass effect for modals */}
</div>
```

**CSS:**
```css
.glass-strong {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 20px 64px 0 rgba(31, 38, 135, 0.25),
    0 10px 32px 0 rgba(31, 38, 135, 0.15);
}
```

---

### Variant 4: Header Glass (Top Navigation)

**Use Case**: Fixed header with backdrop blur

```tsx
<header className="
  fixed top-0 left-0 right-0
  bg-white/80 backdrop-blur-md
  border-b border-white/20
  shadow-sm
  z-20
">
  {/* Header with glassmorphism */}
</header>
```

**CSS:**
```css
.glass-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px) saturate(150%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
```

---

## Dark Mode Adaptations

### Dark Mode Glass Cards

```tsx
{/* Light mode */}
<div className="
  bg-white/10 backdrop-blur-md
  border border-white/20
  dark:bg-black/30 dark:backdrop-blur-lg
  dark:border-white/10
  rounded-lg
">
```

**CSS:**
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .glass-card {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(16px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 8px 32px 0 rgba(0, 0, 0, 0.4),
    0 4px 16px 0 rgba(0, 0, 0, 0.2);
}
```

---

## Background Patterns for Glassmorphism

### Gradient Backgrounds

**Light Mode:**
```css
body {
  background: linear-gradient(
    135deg,
    #667eea 0%,
    #764ba2 100%
  );
}

/* Alternative: Subtle gradient */
body {
  background: linear-gradient(
    to bottom right,
    #fafafa 0%,
    #e5e5e5 100%
  );
}
```

**Dark Mode:**
```css
body {
  background: linear-gradient(
    135deg,
    #1a1a2e 0%,
    #16213e 100%
  );
}
```

### Animated Gradient (Optional)

```css
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

body {
  background: linear-gradient(
    -45deg,
    #667eea,
    #764ba2,
    #f093fb,
    #4facfe
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```

---

## Component-Specific Glass Styles

### Task Card with Glass

```tsx
export function TaskCard({ task }: TaskCardProps) {
  return (
    <motion.div
      className="
        glass-standard
        p-6 rounded-lg
        hover:scale-[1.02]
        transition-transform duration-200
      "
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <input type="checkbox" className="h-5 w-5" />
          <h3 className="font-semibold text-neutral-900">{task.title}</h3>
        </div>

        <button className="
          bg-white/50 hover:bg-white/70
          backdrop-blur-sm
          px-3 py-1 rounded-md
          text-sm
          transition-colors duration-200
        ">
          Edit
        </button>
      </div>

      <p className="text-neutral-600 mt-2">{task.description}</p>
    </motion.div>
  );
}
```

### Modal with Strong Glass

```tsx
export function Modal({ isOpen, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay with subtle glass */}
      <div
        className="absolute inset-0 bg-black/20 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal with strong glass */}
      <div className="
        relative
        glass-strong
        max-w-lg w-full
        rounded-xl p-6
        animate-in fade-in zoom-in duration-200
      ">
        {children}
      </div>
    </div>
  );
}
```

### Dropdown Menu with Glass

```tsx
export function Dropdown({ isOpen, items }: DropdownProps) {
  if (!isOpen) return null;

  return (
    <div className="
      absolute top-full right-0 mt-2
      glass-standard
      rounded-lg
      shadow-xl
      min-w-[200px]
      py-2
      z-30
    ">
      {items.map(item => (
        <button
          key={item.id}
          className="
            w-full px-4 py-2 text-left
            hover:bg-white/30
            transition-colors duration-150
          "
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
```

---

## Browser Compatibility

### Backdrop Filter Support

**Supported:**
- Chrome 76+ ✅
- Safari 9+ ✅
- Edge 79+ ✅
- Firefox 103+ ✅

**Fallback for Unsupported Browsers:**
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);

  /* Fallback: Solid background if backdrop-filter not supported */
  @supports not (backdrop-filter: blur(12px)) {
    background: rgba(255, 255, 255, 0.95);
  }
}
```

---

## Performance Optimization

### GPU Acceleration

```css
.glass-card {
  /* Force GPU acceleration */
  transform: translateZ(0);
  will-change: transform;

  /* Optimize backdrop-filter */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px); /* Safari */
}
```

### Avoid Overuse

**DO:**
- Use glass effects for 5-10 key UI elements
- Apply to cards, modals, headers
- Maintain performance at 60fps

**DON'T:**
- Apply glass to every element (causes lag)
- Stack multiple blur layers (expensive)
- Use on rapidly animating elements

---

## Implementation Checklist

When implementing glassmorphism:

- ✅ Set colorful/gradient background behind glass elements
- ✅ Use appropriate opacity (10%-70% depending on prominence)
- ✅ Apply backdrop-filter with blur (8px-20px)
- ✅ Add subtle border (1px solid with 10%-30% opacity)
- ✅ Include shadows for depth
- ✅ Test in light and dark modes
- ✅ Verify 60fps performance on lower-end devices
- ✅ Add fallback for unsupported browsers
- ✅ Ensure text contrast meets WCAG 2.1 AA (4.5:1 minimum)

---

## Real-World Examples

### Login Page with Glass

```tsx
export function LoginPage() {
  return (
    <div className="
      min-h-screen
      bg-linear-to-br from-purple-500 to-pink-500
      flex items-center justify-center
      p-4
    ">
      <div className="
        glass-strong
        max-w-md w-full
        rounded-2xl p-8
      ">
        <h1 className="text-3xl font-bold text-white mb-6">Welcome Back</h1>

        <form className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            className="
              w-full px-4 py-3
              bg-white/20 backdrop-blur-sm
              border border-white/30
              rounded-lg
              text-white placeholder:text-white/60
              focus:outline-none focus:ring-2 focus:ring-white/50
            "
          />

          <input
            type="password"
            placeholder="Password"
            className="
              w-full px-4 py-3
              bg-white/20 backdrop-blur-sm
              border border-white/30
              rounded-lg
              text-white placeholder:text-white/60
              focus:outline-none focus:ring-2 focus:ring-white/50
            "
          />

          <button className="
            w-full py-3
            bg-white/30 hover:bg-white/40
            backdrop-blur-sm
            border border-white/40
            rounded-lg
            text-white font-semibold
            transition-colors duration-200
          ">
            Log In
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## Success Criteria

Glassmorphism implementation is complete when:

- ✅ All glass components render with frosted effect
- ✅ Gradients/backgrounds visible behind glass
- ✅ Blur strength appropriate for each use case
- ✅ Dark mode glass styles work correctly
- ✅ Performance remains at 60fps
- ✅ Text contrast meets accessibility standards
- ✅ Fallbacks work in unsupported browsers
- ✅ Hover states enhance glass effect

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
