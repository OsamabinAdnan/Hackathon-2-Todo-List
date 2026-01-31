import { Task } from '@/lib/types';

// Reminder thresholds in milliseconds
const THRESHOLDS: Record<string, number[]> = {
  yearly: [
    30 * 24 * 60 * 60 * 1000,  // 1 month before
    7 * 24 * 60 * 60 * 1000,   // 1 week before
    24 * 60 * 60 * 1000,       // 1 day before
    60 * 60 * 1000,            // 1 hour before
  ],
  monthly: [
    7 * 24 * 60 * 60 * 1000,   // 1 week before
    24 * 60 * 60 * 1000,       // 1 day before
    60 * 60 * 1000,            // 1 hour before
  ],
  weekly: [
    24 * 60 * 60 * 1000,       // 1 day before
    60 * 60 * 1000,            // 1 hour before
  ],
  daily: [
    60 * 60 * 1000,            // 1 hour before
  ],
};

// Parse local date string without timezone conversion
function parseLocalDate(dateString: string): Date {
  // Parse the date as local time by manually extracting parts
  const parts = dateString.match(/(\d{4})-(\d{2})-(\d{2})T?(\d{2}):(\d{2}):?(\d{2})?/);
  if (!parts) return new Date();

  // Extract parts
  const year = parseInt(parts[1], 10);
  const month = parseInt(parts[2], 10) - 1; // JS months are 0-indexed
  const day = parseInt(parts[3], 10);
  const hour = parts[4] ? parseInt(parts[4], 10) : 0;
  const minute = parts[5] ? parseInt(parts[5], 10) : 0;
  const second = parts[6] ? parseInt(parts[6], 10) : 0;

  return new Date(year, month, day, hour, minute, second);
}

// Format time remaining as human readable
export function formatTimeRemaining(ms: number): string {
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

// Get the recurrence pattern, handling null/undefined
function getRecurrencePattern(task: Task): string {
  const pattern = task.recurrence_pattern;
  if (!pattern || pattern === null || pattern === undefined) return 'none';
  return String(pattern).toLowerCase();
}

// Check if task should show reminder based on thresholds
export function shouldShowReminder(task: Task): boolean {
  // Skip completed tasks
  if (task.status === 'completed') return false;

  // Skip tasks without due date
  if (!task.due_date) return false;

  const now = new Date();
  const dueDate = parseLocalDate(task.due_date);
  const timeUntilDue = dueDate.getTime() - now.getTime();

  // Task must be in the future (at least 1 minute from now)
  if (timeUntilDue <= 0) return false;

  // Get recurrence pattern
  const pattern = getRecurrencePattern(task);
  const thresholds = THRESHOLDS[pattern] || [];

  // If no thresholds for this pattern, don't show reminder
  if (thresholds.length === 0) return false;

  // Check if we're within any threshold window
  return thresholds.some(threshold => timeUntilDue <= threshold);
}

// Get the earliest upcoming task with reminder
export function getNextReminderTask(tasks: Task[]): { task: Task; timeRemaining: number } | null {
  const now = new Date();
  let nextTask: { task: Task; timeRemaining: number } | null = null;

  for (const task of tasks) {
    if (!shouldShowReminder(task)) continue;

    const dueDate = parseLocalDate(task.due_date!);
    const timeUntilDue = dueDate.getTime() - now.getTime();

    if (!nextTask || timeUntilDue < nextTask.timeRemaining) {
      nextTask = { task, timeRemaining: timeUntilDue };
    }
  }

  return nextTask;
}
