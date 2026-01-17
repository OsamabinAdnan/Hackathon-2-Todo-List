// Notification utility functions

// Reminder thresholds based on spec:
// - Daily tasks: 1 hour before
// - Weekly tasks: 1 day and 1 hour before
// - Monthly tasks: 1 week, 1 day, and 1 hour before
// - Yearly tasks: 1 month, 1 week, 1 day, and 1 hour before

export const REMINDER_THRESHOLDS = {
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

export const requestNotificationPermission = async (): Promise<NotificationPermission> => {
  if (!('Notification' in window)) {
    console.log('This browser does not support desktop notification');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return Notification.permission;
  }

  return await Notification.requestPermission();
};

export const showNotification = (title: string, options?: NotificationOptions): void => {
  if (Notification.permission === 'granted') {
    try {
      new Notification(title, options);
    } catch (error) {
      console.error('Error showing notification:', error);
    }
  }
};

// Get reminder thresholds based on recurrence pattern
export const getReminderThresholds = (recurrencePattern: string): number[] => {
  switch (recurrencePattern) {
    case 'yearly':
      return REMINDER_THRESHOLDS.yearly;
    case 'monthly':
      return REMINDER_THRESHOLDS.monthly;
    case 'weekly':
      return REMINDER_THRESHOLDS.weekly;
    case 'daily':
      return REMINDER_THRESHOLDS.daily;
    default:
      return [];
  }
};

// Format reminder time for notification
export const formatReminderTime = (threshold: number): string => {
  if (threshold >= 30 * 24 * 60 * 60 * 1000) {
    return '1 month';
  } else if (threshold >= 7 * 24 * 60 * 60 * 1000) {
    return '1 week';
  } else if (threshold >= 24 * 60 * 60 * 1000) {
    return '1 day';
  } else if (threshold >= 60 * 60 * 1000) {
    return '1 hour';
  }
  return '';
};

// Check if a reminder should be triggered
export const shouldTriggerReminder = (
  dueDate: string | undefined,
  recurrencePattern: string,
  threshold: number,
  lastNotified: Map<string, number>
): boolean => {
  if (!dueDate) return false;

  const now = new Date();
  const taskDueDate = new Date(dueDate);
  const timeUntilDue = taskDueDate.getTime() - now.getTime();

  // Don't show if task is past due
  if (timeUntilDue <= 0) return false;

  // Check if we're within the threshold window and haven't notified for this threshold
  const reminderKey = `${dueDate}-${threshold}`;
  const lastNotificationTime = lastNotified.get(reminderKey);

  if (timeUntilDue <= threshold) {
    // Check if we've already notified for this threshold (within the reminder window)
    if (lastNotificationTime) {
      const timeSinceLastNotification = now.getTime() - lastNotificationTime;
      // Only notify once per threshold, then remind every 30 minutes
      if (timeSinceLastNotification < 30 * 60 * 1000) {
        return false;
      }
    }
    return true;
  }

  return false;
};

// Send a task reminder notification
export const sendTaskReminder = (
  taskTitle: string,
  recurrencePattern: string,
  timeUntilDue: number
): void => {
  let timeMessage = '';

  // Find which threshold we're at
  const thresholds = getReminderThresholds(recurrencePattern);
  for (const threshold of thresholds) {
    if (timeUntilDue <= threshold) {
      timeMessage = formatReminderTime(threshold);
      break;
    }
  }

  if (!timeMessage) {
    // Default to generic message if no threshold matches
    if (timeUntilDue <= 60 * 60 * 1000) {
      timeMessage = 'less than 1 hour';
    } else if (timeUntilDue <= 24 * 60 * 60 * 1000) {
      timeMessage = 'less than 1 day';
    } else {
      timeMessage = 'soon';
    }
  }

  showNotification('Task Reminder', {
    body: `"${taskTitle}" is due in ${timeMessage}`,
    icon: '/favicon.ico',
    tag: `reminder-${taskTitle}-${Date.now()}`,
    requireInteraction: false,
  });
};

// Check if a task is due soon (within 60 minutes)
export const isDueSoon = (dueDate: string | undefined): boolean => {
  if (!dueDate) return false;

  const now = new Date();
  const taskDueDate = new Date(dueDate);
  const timeDiff = taskDueDate.getTime() - now.getTime(); // difference in milliseconds
  const minutesDiff = Math.floor(timeDiff / (1000 * 60)); // convert to minutes

  // Task is due within 60 minutes but not overdue
  return minutesDiff > 0 && minutesDiff <= 60;
};

// Check if a task is overdue
export const isOverdue = (dueDate: string | undefined, status: string): boolean => {
  if (!dueDate || status === 'completed') return false;

  const now = new Date();
  const taskDueDate = new Date(dueDate);

  return taskDueDate < now;
};

// Format time for display (e.g., "due in 30 minutes" or "overdue by 2 hours")
export const formatTimeMessage = (dueDate: string | undefined): string => {
  if (!dueDate) return '';

  const now = new Date();
  const taskDueDate = new Date(dueDate);
  const timeDiff = taskDueDate.getTime() - now.getTime(); // difference in milliseconds
  const absTimeDiff = Math.abs(timeDiff);
  const minutesDiff = Math.floor(absTimeDiff / (1000 * 60));
  const hoursDiff = Math.floor(absTimeDiff / (1000 * 60 * 60));
  const daysDiff = Math.floor(absTimeDiff / (1000 * 60 * 60 * 24));

  if (minutesDiff < 1) {
    return 'due now';
  } else if (minutesDiff < 60) {
    const plural = minutesDiff === 1 ? '' : 's';
    return timeDiff > 0 ? `due in ${minutesDiff} minute${plural}` : `overdue by ${minutesDiff} minute${plural}`;
  } else if (hoursDiff < 24) {
    const plural = hoursDiff === 1 ? '' : 's';
    return timeDiff > 0 ? `due in ${hoursDiff} hour${plural}` : `overdue by ${hoursDiff} hour${plural}`;
  } else {
    const plural = daysDiff === 1 ? '' : 's';
    return timeDiff > 0 ? `due in ${daysDiff} day${plural}` : `overdue by ${daysDiff} day${plural}`;
  }
};