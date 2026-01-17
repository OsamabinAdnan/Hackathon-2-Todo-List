'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Task } from '@/lib/types';

interface ReminderBannerProps {
  tasks: Task[];
  className?: string;
}

interface UpcomingTask {
  task: Task;
  timeRemaining: number;
}

// Parse local date string without timezone conversion
function parseLocalDate(dateString: string): Date {
  const parts = dateString.match(/(\d{4})-(\d{2})-(\d{2})T?(\d{2}):(\d{2}):?(\d{2})?/);
  if (!parts) return new Date();

  const year = parseInt(parts[1], 10);
  const month = parseInt(parts[2], 10) - 1;
  const day = parseInt(parts[3], 10);
  const hour = parts[4] ? parseInt(parts[4], 10) : 0;
  const minute = parts[5] ? parseInt(parts[5], 10) : 0;
  const second = parts[6] ? parseInt(parts[6], 10) : 0;

  return new Date(year, month, day, hour, minute, second);
}

// Format time remaining as human readable
function formatTimeRemaining(ms: number): string {
  if (ms <= 0) return 'Due now';

  const minutes = Math.floor(ms / (1000 * 60));
  const hours = Math.floor(ms / (1000 * 60 * 60));
  const days = Math.floor(ms / (1000 * 60 * 60 * 24));
  const weeks = Math.floor(ms / (1000 * 60 * 60 * 24 * 7));
  const months = Math.floor(ms / (1000 * 60 * 60 * 24 * 30));

  if (months > 0) return months === 1 ? '1 month' : `${months} months`;
  if (weeks > 0) return weeks === 1 ? '1 week' : `${weeks} weeks`;
  if (days > 0) return days === 1 ? '1 day' : `${days} days`;
  if (hours > 0) return hours === 1 ? '1 hour' : `${hours} hours`;
  return minutes <= 1 ? '1 minute' : `${minutes} minutes`;
}

export function ReminderBanner({ tasks, className }: ReminderBannerProps) {
  const [upcomingTasks, setUpcomingTasks] = useState<UpcomingTask[]>([]);

  useEffect(() => {
    const now = new Date();
    const upcoming: UpcomingTask[] = [];

    // Get all incomplete tasks with due dates
    for (const task of tasks) {
      if (!task.due_date || task.status === 'completed') continue;

      const dueDate = parseLocalDate(task.due_date);
      const timeRemaining = dueDate.getTime() - now.getTime();

      // Only show tasks that are in the future
      if (timeRemaining > 0) {
        upcoming.push({ task, timeRemaining });
      }
    }

    // Sort by time remaining (soonest first)
    upcoming.sort((a, b) => a.timeRemaining - b.timeRemaining);

    setUpcomingTasks(upcoming.slice(0, 5)); // Show top 5 upcoming tasks
  }, [tasks]);

  if (upcomingTasks.length === 0) return null;

  const firstTask = upcomingTasks[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'flex items-center gap-2 xs:gap-3 px-2.5 xs:px-3 sm:px-4 py-2 xs:py-2.5 sm:py-3 rounded-xl border shadow-lg',
        'bg-red-500/10 border-red-500/30 dark:bg-red-500/20 dark:border-red-500/40',
        className
      )}
    >
      {/* Bell icon */}
      <div className="flex-shrink-0 w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 rounded-full bg-red-500/20 text-red-600 dark:text-red-400 flex items-center justify-center">
        <Bell className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4" />
      </div>

      {/* Message */}
      <div className="flex-1 min-w-0">
        <p className="text-[11px] xs:text-xs sm:text-sm font-medium text-foreground leading-tight font-mono">
          Your next task <span className="font-semibold">"{firstTask.task.title}"</span> is due in{' '}
          <span className="font-semibold text-red-600 dark:text-red-400">
            {formatTimeRemaining(firstTask.timeRemaining)}
          </span>
        </p>
        {upcomingTasks.length > 1 && (
          <p className="text-[10px] xs:text-xs text-muted-foreground mt-0.5 font-mono">
            +{upcomingTasks.length - 1} more upcoming task{upcomingTasks.length - 1 > 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* Clock icon */}
      <Clock className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 text-red-600 dark:text-red-400 flex-shrink-0" />
    </motion.div>
  );
}

// Component to show list of all upcoming tasks
export function UpcomingTasksList({ tasks, className }: ReminderBannerProps) {
  const [upcomingTasks, setUpcomingTasks] = useState<UpcomingTask[]>([]);

  useEffect(() => {
    const now = new Date();
    const upcoming: UpcomingTask[] = [];

    for (const task of tasks) {
      if (!task.due_date || task.status === 'completed') continue;

      const dueDate = parseLocalDate(task.due_date);
      const timeRemaining = dueDate.getTime() - now.getTime();

      if (timeRemaining > 0) {
        upcoming.push({ task, timeRemaining });
      }
    }

    upcoming.sort((a, b) => a.timeRemaining - b.timeRemaining);
    setUpcomingTasks(upcoming);
  }, [tasks]);

  if (upcomingTasks.length === 0) return null;

  return (
    <div className={cn('space-y-2', className)}>
      {upcomingTasks.map((item, index) => (
        <motion.div
          key={item.task.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-xl border',
            'bg-primary/5 border-primary/20 dark:bg-primary/10 dark:border-primary/20'
          )}
        >
          <Clock className="w-4 h-4 text-primary flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {item.task.title}
            </p>
            <p className="text-xs text-muted-foreground capitalize">
              {item.task.recurrence_pattern !== 'none' ? `${item.task.recurrence_pattern} task` : 'One-time task'}
            </p>
          </div>
          <span className="text-sm font-semibold text-primary whitespace-nowrap">
            {formatTimeRemaining(item.timeRemaining)}
          </span>
        </motion.div>
      ))}
    </div>
  );
}
