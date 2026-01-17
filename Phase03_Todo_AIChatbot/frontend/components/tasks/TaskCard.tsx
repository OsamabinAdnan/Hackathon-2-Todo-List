'use client';

import { Task } from '@/lib/types';
import { Checkbox } from '@/components/ui/checkbox';
import { PencilIcon, Trash2Icon, CalendarIcon, HashIcon, RepeatIcon } from 'lucide-react';
import { AnimatedTaskItem } from '@/components/ui/animate';
import { cn } from '@/lib/utils';

interface TaskCardProps {
  task: Task;
  index: number;
  viewMode: 'list' | 'grid';
  onToggle: (id: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
}

// Helper to parse local date string without timezone conversion
function parseLocalDate(dateString: string | null | undefined): Date | null {
  if (!dateString) return null;
  // Parse the date as local time by manually extracting parts
  const parts = dateString.match(/(\d{4})-(\d{2})-(\d{2})T?(\d{2}):(\d{2}):?(\d{2})?/);
  if (!parts) return null;

  // Extract parts
  const year = parseInt(parts[1], 10);
  const month = parseInt(parts[2], 10) - 1; // JS months are 0-indexed
  const day = parseInt(parts[3], 10);
  const hour = parts[4] ? parseInt(parts[4], 10) : 0;
  const minute = parts[5] ? parseInt(parts[5], 10) : 0;
  const second = parts[6] ? parseInt(parts[6], 10) : 0;

  return new Date(year, month, day, hour, minute, second);
}

const priorityColors = {
  high: 'bg-danger/20 text-danger border-danger/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  low: 'bg-success/20 text-success border-success/30',
  none: 'bg-muted/20 text-muted-foreground border-border/30',
  HIGH: 'bg-danger/20 text-danger border-danger/30',
  MEDIUM: 'bg-warning/20 text-warning border-warning/30',
  LOW: 'bg-success/20 text-success border-success/30',
  NONE: 'bg-muted/20 text-muted-foreground border-border/30',
};

const tagColors = [
  'bg-blue-500/20 text-blue-600 dark:text-blue-400 border-blue-500/30',
  'bg-purple-500/20 text-purple-600 dark:text-purple-400 border-purple-500/30',
  'bg-pink-500/20 text-pink-600 dark:text-pink-400 border-pink-500/30',
  'bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/30',
  'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 border-yellow-500/30',
  'bg-orange-500/20 text-orange-600 dark:text-orange-400 border-orange-500/30',
  'bg-red-500/20 text-red-600 dark:text-red-400 border-red-500/30',
  'bg-teal-500/20 text-teal-600 dark:text-teal-400 border-teal-500/30',
  'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border-cyan-500/30',
  'bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border-indigo-500/30',
];

const getTagColor = (tag: string, index: number) => {
  // Use hash of tag string to get consistent color for same tag
  const hash = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return tagColors[hash % tagColors.length];
};

export function TaskCard({ task, index, viewMode, onToggle, onEdit, onDelete }: TaskCardProps) {
  const isCompleted = task.status === 'completed';

  return (
    <AnimatedTaskItem
      index={index}
      className={cn(
        "group relative p-5 glass-card rounded-xl border border-border/40 hover:border-primary/30 transition-all duration-300 flex shadow-lg shadow-primary/10 hover:shadow-xl hover:shadow-primary/20 font-mono",
        viewMode === 'grid' ? "flex-col h-full min-h-[220px]" : "flex-row items-start gap-4"
      )}
    >
      <div className="flex items-start gap-3 flex-1 min-w-0 h-full">
        <Checkbox
          checked={isCompleted}
          onCheckedChange={() => onToggle(task.id)}
          className="mt-1.5 h-5 w-5 rounded-md border-primary bg-card/40 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
        />

        <div className="flex-1 flex flex-col h-full min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h3 className={cn(
              "text-sm xs:text-base sm:text-lg font-bold leading-tight transition-all duration-300 truncate font-mono",
              isCompleted ? "text-muted-foreground line-through opacity-70" : "text-foreground"
            )}>
              {task.title}
            </h3>

            <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-1 shrink-0">
              <button
                type="button"
                onClick={() => onEdit(task)}
                className="p-1.5 rounded-lg text-primary hover:text-primary hover:bg-primary/20 bg-primary/10 border border-primary/20 hover:border-primary/40 transition-all font-mono"
                title="Edit Task"
                aria-label="Edit Task"
              >
                <PencilIcon className="h-3.5 w-3.5 xs:h-4 xs:w-4" />
              </button>
              <button
                type="button"
                onClick={() => onDelete(task.id)}
                className="p-1.5 rounded-lg text-danger hover:text-danger hover:bg-danger/20 bg-danger/10 border border-danger/20 hover:border-danger/40 transition-all font-mono"
                title="Delete Task"
                aria-label="Delete Task"
              >
                <Trash2Icon className="h-3.5 w-3.5 xs:h-4 xs:w-4" />
              </button>
            </div>
          </div>

          {task.description && (
            <p className={cn(
              "text-sm text-muted-foreground mb-4 line-clamp-2 font-mono",
              isCompleted && "opacity-60"
            )}>
              {task.description}
            </p>
          )}

          <div className="mt-auto space-y-3">
            <div className="flex flex-wrap gap-2 items-center">
              <span className={cn(
                "px-2.5 py-1 text-[10px] md:text-xs lg:text-sm font-bold uppercase tracking-wider rounded-full border backdrop-blur-md shadow-sm font-mono",
                priorityColors[task.priority] || priorityColors.none
              )}>
                {task.priority}
              </span>

              {task.due_date && (() => {
                const date = parseLocalDate(task.due_date);
                return date ? (
                  <span className="flex items-center gap-1.5 px-2.5 py-1 text-[10px] md:text-xs lg:text-sm font-bold rounded-full bg-primary/10 text-primary border border-primary/20 backdrop-blur-md font-mono">
                    <CalendarIcon className="h-3 w-3 md:h-4 md:w-4" />
                    {date.toLocaleDateString()} {' '}
                    {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                ) : null;
              })()}

              {task.recurrence_pattern && task.recurrence_pattern !== 'none' && (
                <span className="flex items-center gap-1.5 px-2.5 py-1 text-[10px] md:text-xs lg:text-sm font-bold rounded-full bg-purple-500/20 text-purple-600 dark:text-purple-400 border border-purple-500/30 backdrop-blur-md font-mono">
                  <RepeatIcon className="h-3 w-3 md:h-4 md:w-4" />
                  {task.recurrence_pattern}
                </span>
              )}
            </div>

            {task.tags && task.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 md:gap-2">
                {task.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className={cn(
                      "flex items-center gap-1 px-2 py-0.5 md:px-3 md:py-1 text-[10px] md:text-xs lg:text-sm font-bold rounded-md border backdrop-blur-sm font-mono",
                      getTagColor(tag, idx)
                    )}
                  >
                    <HashIcon className="h-2.5 w-2.5 md:h-3 md:w-3" />
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <div className="flex items-center gap-2 text-[10px] text-muted-foreground pt-1 border-t border-border/20 font-mono">
              <span className="flex-1">
                Created: {parseLocalDate(task.created_at)?.toLocaleDateString()} {' '}
                {parseLocalDate(task.created_at)?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) || 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </AnimatedTaskItem>
  );
}