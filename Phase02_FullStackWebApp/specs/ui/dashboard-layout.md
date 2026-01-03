# Dashboard Layout Specification

**Project**: Hackathon II Phase 2 - Todo Full-Stack Web Application
**Purpose**: Define the complete dashboard layout structure and navigation patterns
**Version**: 1.0.0
**Last Updated**: 2026-01-02

---

## Layout Philosophy

Create a **professional, intuitive dashboard experience** with:

- **Clear information hierarchy**: Most important content above the fold
- **Efficient navigation**: Maximum 2 clicks to reach any feature
- **Persistent context**: User always knows where they are
- **Responsive adaptation**: Graceful degradation from desktop to mobile

---

## Desktop Layout (1024px+)

### Structure Overview

```
┌─────────────────────────────────────────────────────────┐
│  Header (64px fixed)                                    │
│  ┌──────────┬──────────────────────────┬──────────────┐│
│  │   Logo   │   Search (global)        │  User Menu   ││
│  └──────────┴──────────────────────────┴──────────────┘│
├───────────┬─────────────────────────────────────────────┤
│           │                                             │
│  Sidebar  │  Main Content Area                          │
│  (240px   │                                             │
│   fixed)  │  ┌────────────────────────────────────┐   │
│           │  │  Page Header (with actions)         │   │
│  [Nav]    │  ├────────────────────────────────────┤   │
│  [Nav]    │  │                                     │   │
│  [Nav]    │  │  Content Cards/Grid                 │   │
│  [Nav]    │  │                                     │   │
│  [Nav]    │  │                                     │   │
│           │  │                                     │   │
│           │  └────────────────────────────────────┘   │
│           │                                             │
└───────────┴─────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Header Bar (Top Navigation)

**Dimensions**: Full width × 64px (fixed)
**Position**: Sticky at top
**Z-index**: `var(--z-sticky)` (20)

**Structure:**
```tsx
<header className="fixed top-0 left-0 right-0 z-20 h-16 bg-white/80 backdrop-blur-md border-b border-neutral-200">
  <div className="flex items-center justify-between h-full px-6">
    {/* Left: Logo */}
    <div className="flex items-center space-x-4">
      <Logo className="h-8 w-auto" />
      <span className="font-mono text-xl font-bold text-neutral-900">TaskFlow</span>
    </div>

    {/* Center: Global Search (desktop only) */}
    <div className="hidden md:block flex-1 max-w-xl mx-8">
      <SearchBar placeholder="Search tasks, tags, or keywords..." />
    </div>

    {/* Right: Actions + User Menu */}
    <div className="flex items-center space-x-4">
      <button className="relative" aria-label="Notifications">
        <BellIcon className="h-6 w-6" />
        <span className="absolute -top-1 -right-1 h-4 w-4 bg-danger-500 rounded-full text-white text-xs flex items-center justify-center">
          3
        </span>
      </button>

      <UserMenu />
    </div>
  </div>
</header>
```

**Key Features:**
- Glassmorphism effect (`bg-white/80 backdrop-blur-md`)
- Search bar centered (collapses on tablet)
- Notification badge with count
- User avatar dropdown

---

#### 2. Sidebar Navigation (Left Panel)

**Dimensions**: 240px × full height (fixed)
**Position**: Fixed left
**Collapse**: Hamburger icon on mobile

**Structure:**
```tsx
<aside className="fixed left-0 top-16 bottom-0 w-60 bg-neutral-50 border-r border-neutral-200 overflow-y-auto">
  <nav className="p-4 space-y-1">
    {/* Primary Navigation */}
    <NavItem icon={HomeIcon} label="Dashboard" href="/dashboard" active />
    <NavItem icon={ListIcon} label="All Tasks" href="/tasks" />
    <NavItem icon={CalendarIcon} label="Calendar" href="/calendar" />
    <NavItem icon={TagIcon} label="Tags" href="/tags" />

    {/* Divider */}
    <hr className="my-4 border-neutral-300" />

    {/* Filter Section */}
    <div className="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
      Filters
    </div>
    <NavItem icon={CircleIcon} label="To Do" badge={12} />
    <NavItem icon={CheckCircleIcon} label="Completed" badge={45} />
    <NavItem icon={AlertCircleIcon} label="Overdue" badge={3} badgeColor="danger" />

    {/* Divider */}
    <hr className="my-4 border-neutral-300" />

    {/* Priority Filters */}
    <div className="px-3 py-2 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
      Priority
    </div>
    <NavItem icon={FlagIcon} label="High" badgeColor="danger" />
    <NavItem icon={FlagIcon} label="Medium" badgeColor="warning" />
    <NavItem icon={FlagIcon} label="Low" badgeColor="success" />

    {/* Divider */}
    <hr className="my-4 border-neutral-300" />

    {/* Bottom Actions */}
    <NavItem icon={SettingsIcon} label="Settings" href="/settings" />
  </nav>
</aside>
```

**NavItem Component:**
```tsx
<a href={href} className={`
  flex items-center justify-between px-3 py-2 rounded-md
  text-sm font-medium
  ${active
    ? 'bg-primary-100 text-primary-700'
    : 'text-neutral-700 hover:bg-neutral-100'
  }
  transition-colors duration-200
`}>
  <div className="flex items-center space-x-3">
    <Icon className="h-5 w-5" />
    <span>{label}</span>
  </div>

  {badge && (
    <span className={`
      px-2 py-0.5 text-xs font-mono rounded-full
      ${badgeColor === 'danger' ? 'bg-danger-100 text-danger-700' : 'bg-neutral-200 text-neutral-700'}
    `}>
      {badge}
    </span>
  )}
</a>
```

**Key Features:**
- Active state highlighting
- Badge counts for filters
- Color-coded priority badges
- Scrollable on overflow
- Smooth hover transitions

---

#### 3. Main Content Area

**Dimensions**: Remaining width (after sidebar) × full height
**Position**: `margin-left: 240px` (desktop), full width (mobile)

**Structure:**
```tsx
<main className="ml-60 mt-16 min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 p-8">
  {/* Page Header */}
  <div className="mb-8">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-4xl font-bold text-neutral-900 mb-2">Dashboard</h1>
        <p className="text-neutral-600">Welcome back, John! You have 12 tasks today.</p>
      </div>

      <button className="btn-primary">
        <PlusIcon className="h-5 w-5 mr-2" />
        New Task
      </button>
    </div>
  </div>

  {/* Stats Cards */}
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <StatCard title="Total Tasks" value={57} icon={ListIcon} trend="+12%" />
    <StatCard title="Completed" value={45} icon={CheckIcon} trend="+8%" />
    <StatCard title="In Progress" value={12} icon={ClockIcon} />
    <StatCard title="Overdue" value={3} icon={AlertIcon} trend="-2" trendColor="success" />
  </div>

  {/* Task List */}
  <div className="glass-card p-6">
    <h2 className="text-2xl font-semibold mb-4">Today's Tasks</h2>
    <TaskList tasks={tasks} />
  </div>
</main>
```

**Key Features:**
- Background gradient for depth
- Stats cards with glassmorphism
- Generous spacing (8-unit grid)
- Clear page hierarchy (H1 → H2 → content)

---

## Tablet Layout (768px - 1023px)

### Changes from Desktop

1. **Sidebar**: Collapses to icons only (64px width)
   ```tsx
   <aside className="w-16">
     <nav>
       <IconButton icon={HomeIcon} tooltip="Dashboard" />
       <IconButton icon={ListIcon} tooltip="All Tasks" />
     </nav>
   </aside>
   ```

2. **Main Content**: Adjusts left margin to 64px

3. **Header Search**: Hidden, accessible via icon
   ```tsx
   <button onClick={openSearchModal}>
     <SearchIcon className="h-6 w-6" />
   </button>
   ```

4. **Grid Layouts**: Reduce columns
   ```tsx
   {/* Stats: 2 columns instead of 4 */}
   <div className="grid grid-cols-2 gap-4">
   ```

---

## Mobile Layout (< 768px)

### Structure Overview

```
┌───────────────────────────────┐
│  Header (56px)                │
│  [Menu] [Logo]    [Search][+] │
├───────────────────────────────┤
│                               │
│  Full-width Content           │
│                               │
│  ┌─────────────────────────┐ │
│  │  Stats (1 column)       │ │
│  ├─────────────────────────┤ │
│  │  Task Cards (stacked)   │ │
│  │                         │ │
│  └─────────────────────────┘ │
│                               │
├───────────────────────────────┤
│  Bottom Nav (56px)            │
│  [Home] [Tasks] [Add] [More]  │
└───────────────────────────────┘
```

### Mobile-Specific Changes

1. **Header Height**: Reduced to 56px
2. **Sidebar**: Off-canvas drawer (swipe from left or hamburger icon)
3. **Bottom Navigation Bar**: Primary navigation
   ```tsx
   <nav className="fixed bottom-0 left-0 right-0 h-14 bg-white border-t border-neutral-200 flex justify-around items-center">
     <IconButton icon={HomeIcon} label="Home" active />
     <IconButton icon={ListIcon} label="Tasks" />
     <button className="btn-primary rounded-full h-12 w-12 -mt-6 shadow-xl">
       <PlusIcon className="h-6 w-6" />
     </button>
     <IconButton icon={CalendarIcon} label="Calendar" />
     <IconButton icon={MoreIcon} label="More" />
   </nav>
   ```

4. **Floating Action Button**: Centered in bottom nav

5. **Content Padding**: Reduced to 16px

6. **Stats Grid**: Single column

---

## Layout Components

### StatCard Component

```tsx
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ComponentType;
  trend?: string;
  trendColor?: 'success' | 'danger';
}

export function StatCard({ title, value, icon: Icon, trend, trendColor = 'success' }: StatCardProps) {
  return (
    <div className="glass-card p-6 hover:shadow-xl transition-shadow duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className="h-12 w-12 rounded-lg bg-primary-100 flex items-center justify-center">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>

        {trend && (
          <span className={`text-sm font-mono ${trendColor === 'success' ? 'text-success-600' : 'text-danger-600'}`}>
            {trend}
          </span>
        )}
      </div>

      <h3 className="text-3xl font-bold font-mono text-neutral-900 mb-1">{value}</h3>
      <p className="text-sm text-neutral-600">{title}</p>
    </div>
  );
}
```

### PageHeader Component

```tsx
interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-4xl font-bold text-neutral-900 mb-2">{title}</h1>
        {description && <p className="text-neutral-600">{description}</p>}
      </div>
      {action}
    </div>
  );
}
```

---

## Navigation Patterns

### Breadcrumbs (for deep navigation)

```tsx
<nav aria-label="Breadcrumb" className="mb-6">
  <ol className="flex items-center space-x-2 text-sm">
    <li><a href="/dashboard" className="text-neutral-600 hover:text-neutral-900">Dashboard</a></li>
    <li className="text-neutral-400">/</li>
    <li><a href="/tasks" className="text-neutral-600 hover:text-neutral-900">Tasks</a></li>
    <li className="text-neutral-400">/</li>
    <li className="text-neutral-900 font-medium" aria-current="page">Edit Task #123</li>
  </ol>
</nav>
```

### Tabs (for page sections)

```tsx
<div className="border-b border-neutral-200 mb-6">
  <nav className="flex space-x-8">
    <button className="border-b-2 border-primary-500 pb-3 text-primary-600 font-medium">
      Active Tasks
    </button>
    <button className="border-b-2 border-transparent pb-3 text-neutral-600 hover:text-neutral-900">
      Completed
    </button>
    <button className="border-b-2 border-transparent pb-3 text-neutral-600 hover:text-neutral-900">
      Archived
    </button>
  </nav>
</div>
```

---

## Empty States

### No Tasks

```tsx
<div className="text-center py-12">
  <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-neutral-100 mb-4">
    <InboxIcon className="h-8 w-8 text-neutral-400" />
  </div>

  <h3 className="text-xl font-semibold text-neutral-900 mb-2">No tasks yet</h3>
  <p className="text-neutral-600 mb-6 max-w-sm mx-auto">
    Get started by creating your first task. Stay organized and productive!
  </p>

  <button className="btn-primary">
    <PlusIcon className="h-5 w-5 mr-2" />
    Create Task
  </button>
</div>
```

---

## Loading States

### Skeleton Loader

```tsx
<div className="glass-card p-6 animate-pulse">
  <div className="h-6 bg-neutral-200 rounded w-1/3 mb-4"></div>
  <div className="space-y-3">
    <div className="h-4 bg-neutral-200 rounded w-full"></div>
    <div className="h-4 bg-neutral-200 rounded w-5/6"></div>
    <div className="h-4 bg-neutral-200 rounded w-4/6"></div>
  </div>
</div>
```

---

## Accessibility

### Landmark Roles

```tsx
<div className="app">
  <header role="banner">...</header>
  <nav role="navigation" aria-label="Main navigation">...</nav>
  <main role="main">...</main>
  <aside role="complementary">...</aside>
  <footer role="contentinfo">...</footer>
</div>
```

### Skip Navigation Link

```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-500 text-white px-4 py-2 rounded-md z-50">
  Skip to main content
</a>
```

---

## Success Criteria

Dashboard layout is complete when:

- ✅ All layouts (desktop, tablet, mobile) render correctly
- ✅ Navigation is intuitive (user testing confirms)
- ✅ Sidebar collapses gracefully on smaller screens
- ✅ Bottom nav is accessible on mobile
- ✅ All interactive elements have proper focus states
- ✅ Breadcrumbs work for deep navigation
- ✅ Empty states guide users to take action
- ✅ Loading skeletons prevent layout shifts

---

**Version**: 1.0.0
**Last Updated**: 2026-01-02
**Owner**: Phase 2 Development Team
