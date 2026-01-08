# Component Templates

Complete, production-ready component examples following Next.js 15+, TypeScript, Tailwind CSS, and accessibility best practices.

## Atomic Component: Button with Variants

```typescript
// components/ui/Button.tsx
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary-500 text-white hover:bg-primary-600 dark:bg-primary-400 dark:hover:bg-primary-500",
        destructive: "bg-red-500 text-white hover:bg-red-600",
        outline: "border border-neutral-200 bg-transparent hover:bg-neutral-100 dark:border-zinc-700 dark:hover:bg-zinc-800",
        ghost: "hover:bg-neutral-100 dark:hover:bg-zinc-800",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

**Usage:**
```tsx
<Button>Default Button</Button>
<Button variant="destructive" size="sm">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="ghost" size="icon" aria-label="More options">
  <MoreVerticalIcon className="h-4 w-4" />
</Button>
```

## Feature Component: TaskCard with Glassmorphism

```typescript
// components/features/TaskCard.tsx
'use client';

import { Task } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckIcon, PencilIcon, TrashIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TaskCardProps {
  task: Task;
  onToggle: (taskId: string) => Promise<void>;
  onEdit?: (taskId: string) => void;
  onDelete: (taskId: string) => Promise<void>;
  className?: string;
}

export function TaskCard({ task, onToggle, onEdit, onDelete, className }: TaskCardProps) {
  const priorityColors = {
    HIGH: "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20",
    MEDIUM: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
    LOW: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
    NONE: "bg-neutral-500/10 text-neutral-700 dark:text-neutral-400 border-neutral-500/20",
  };

  return (
    <Card
      className={cn(
        "group",
        "bg-white/10 dark:bg-black/30",
        "backdrop-blur-md",
        "border border-white/20 dark:border-white/10",
        "hover:shadow-xl",
        "transition-all duration-300",
        task.completed && "opacity-60",
        className
      )}
    >
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className={cn("text-lg", task.completed && "line-through")}>
            {task.title}
          </span>
          <Badge className={cn("text-xs", priorityColors[task.priority])}>
            {task.priority}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          {task.description || "No description"}
        </p>

        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {task.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}

        {task.due_date && (
          <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-3">
            Due: {new Date(task.due_date).toLocaleDateString()}
          </p>
        )}
      </CardContent>

      <CardFooter className="flex justify-between">
        <Button
          onClick={() => onToggle(task.id)}
          size="sm"
          variant={task.completed ? "outline" : "default"}
          className="gap-2"
          aria-label={task.completed ? "Mark task incomplete" : "Mark task complete"}
        >
          <CheckIcon className="h-4 w-4" aria-hidden="true" />
          {task.completed ? "Undo" : "Complete"}
        </Button>

        <div className="flex gap-2">
          {onEdit && (
            <Button
              onClick={() => onEdit(task.id)}
              size="sm"
              variant="ghost"
              aria-label="Edit task"
            >
              <PencilIcon className="h-4 w-4" aria-hidden="true" />
            </Button>
          )}
          <Button
            onClick={() => onDelete(task.id)}
            size="sm"
            variant="ghost"
            className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
            aria-label="Delete task"
          >
            <TrashIcon className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
```

**Usage:**
```tsx
<TaskCard
  task={task}
  onToggle={handleToggle}
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

## Form Component: TaskForm with Validation

```typescript
// components/features/TaskForm.tsx
'use client';

import { useState } from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  description: z.string().max(1000, "Description too long").optional(),
  priority: z.enum(["HIGH", "MEDIUM", "LOW", "NONE"]),
  tags: z.string().optional(), // Comma-separated tags
  due_date: z.string().optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

export interface TaskFormProps {
  initialData?: Partial<TaskFormData>;
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
}

export function TaskForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = "Create Task"
}: TaskFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: initialData,
  });

  const priority = watch("priority");

  const onSubmitHandler = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmitHandler)} className="space-y-6">
      {/* Title Field */}
      <div className="space-y-2">
        <Label htmlFor="title">
          Task Title <span className="text-red-500">*</span>
        </Label>
        <Input
          id="title"
          {...register("title")}
          placeholder="Enter task title"
          aria-required="true"
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? "title-error" : "title-help"}
          className={errors.title ? "border-red-500" : ""}
        />
        {errors.title && (
          <p id="title-error" className="text-sm text-red-500" role="alert">
            {errors.title.message}
          </p>
        )}
        {!errors.title && (
          <p id="title-help" className="text-sm text-neutral-500">
            Brief description of your task (required)
          </p>
        )}
      </div>

      {/* Description Field */}
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          {...register("description")}
          placeholder="Add more details about the task"
          rows={4}
          aria-describedby="description-help"
        />
        <p id="description-help" className="text-sm text-neutral-500">
          Optional: Add additional context or notes
        </p>
      </div>

      {/* Priority Field */}
      <div className="space-y-2">
        <Label htmlFor="priority">Priority</Label>
        <Select
          value={priority}
          onValueChange={(value) => setValue("priority", value as any)}
        >
          <SelectTrigger id="priority" aria-label="Select task priority">
            <SelectValue placeholder="Select priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="HIGH">High</SelectItem>
            <SelectItem value="MEDIUM">Medium</SelectItem>
            <SelectItem value="LOW">Low</SelectItem>
            <SelectItem value="NONE">None</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tags Field */}
      <div className="space-y-2">
        <Label htmlFor="tags">Tags</Label>
        <Input
          id="tags"
          {...register("tags")}
          placeholder="work, urgent, meeting (comma-separated)"
          aria-describedby="tags-help"
        />
        <p id="tags-help" className="text-sm text-neutral-500">
          Separate tags with commas (max 20 characters each)
        </p>
      </div>

      {/* Due Date Field */}
      <div className="space-y-2">
        <Label htmlFor="due_date">Due Date</Label>
        <Input
          id="due_date"
          type="datetime-local"
          {...register("due_date")}
          aria-describedby="due-date-help"
        />
        <p id="due-date-help" className="text-sm text-neutral-500">
          Optional: Set a deadline for this task
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-4 pt-4">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
```

**Usage:**
```tsx
<TaskForm
  onSubmit={handleCreateTask}
  onCancel={() => setIsModalOpen(false)}
  submitLabel="Create Task"
/>

{/* Edit mode */}
<TaskForm
  initialData={{
    title: task.title,
    description: task.description,
    priority: task.priority
  }}
  onSubmit={handleUpdateTask}
  submitLabel="Update Task"
/>
```

## Layout Component: DashboardLayout with Sidebar

```typescript
// components/layouts/DashboardLayout.tsx
import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-linear-to-br from-neutral-50 to-neutral-100 dark:from-zinc-900 dark:to-zinc-950">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="lg:ml-60">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main
          id="main-content"
          className="mt-16 p-4 sm:p-6 md:p-8"
          role="main"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
```

**Usage:**
```tsx
// app/dashboard/page.tsx
import { DashboardLayout } from "@/components/layouts/DashboardLayout";

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      {/* Dashboard content */}
    </DashboardLayout>
  );
}
```
