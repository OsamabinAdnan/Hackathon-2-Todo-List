'use client';

import { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';
import {
  requestNotificationPermission,
  showNotification,
  isDueSoon,
  isOverdue,
  formatTimeMessage,
  getReminderThresholds,
  shouldTriggerReminder,
  sendTaskReminder
} from '@/lib/notifications';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: 'high' | 'medium' | 'low' | 'none';
  due_date?: string;
  recurrence_pattern?: 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly';
  tags: string[];
  created_at: string;
  completed_at?: string;
}

interface NotificationContextType {
  notificationPermission: NotificationPermission;
  requestPermission: () => Promise<NotificationPermission>;
  showNotification: (title: string, options?: NotificationOptions) => void;
  checkAndNotify: (tasks: Task[]) => void;
  checkScheduledReminders: (tasks: Task[]) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider = ({ children }: NotificationProviderProps) => {
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermission>('default');
  // Track when we last sent notifications for each threshold to avoid spam
  const lastNotifiedRef = useRef<Map<string, number>>(new Map());

  useEffect(() => {
    // Check current notification permission
    if ('Notification' in window) {
      const id = window.setTimeout(
        () => setNotificationPermission(Notification.permission),
        0
      );
      return () => window.clearTimeout(id);
    }
  }, []);

  const requestPermission = async (): Promise<NotificationPermission> => {
    const permission = await requestNotificationPermission();
    setNotificationPermission(permission);
    return permission;
  };

  const showNotificationFunc = (title: string, options?: NotificationOptions) => {
    showNotification(title, options);
  };

  const checkAndNotify = (tasks: Task[]) => {
    if (notificationPermission !== 'granted') {
      return;
    }

    tasks.forEach(task => {
      // Check for overdue tasks
      if (isOverdue(task.due_date, task.status)) {
        showNotification(`Overdue Task: ${task.title}`, {
          body: `This task was due ${formatTimeMessage(task.due_date)}`,
          icon: '/favicon.ico',
          tag: `overdue-${task.id}`
        });
      }

      // Check for tasks due soon (within 60 minutes)
      if (isDueSoon(task.due_date)) {
        showNotification(`Task Due Soon: ${task.title}`, {
          body: `This task is ${formatTimeMessage(task.due_date)}`,
          icon: '/favicon.ico',
          tag: `due-soon-${task.id}`
        });
      }
    });
  };

  // Check for scheduled reminders based on recurrence pattern
  const checkScheduledReminders = (tasks: Task[]) => {
    if (notificationPermission !== 'granted') {
      return;
    }

    const lastNotified = lastNotifiedRef.current;
    const now = Date.now();

    tasks.forEach(task => {
      // Skip completed tasks or tasks without due dates
      if (!task.due_date || task.status === 'completed') {
        return;
      }

      const recurrencePattern = task.recurrence_pattern || 'none';
      const thresholds = getReminderThresholds(recurrencePattern);
      const dueDate = new Date(task.due_date);
      const timeUntilDue = dueDate.getTime() - now;

      // Skip if task is past due
      if (timeUntilDue <= 0) {
        return;
      }

      // Check each threshold
      thresholds.forEach(threshold => {
        if (shouldTriggerReminder(task.due_date, recurrencePattern, threshold, lastNotified)) {
          // Send the reminder notification
          sendTaskReminder(task.title, recurrencePattern, timeUntilDue);

          // Update last notified time for this threshold
          const reminderKey = `${task.due_date}-${threshold}`;
          lastNotified.set(reminderKey, now);

          console.log(`Reminder sent for "${task.title}" - due in ${Math.round(timeUntilDue / (1000 * 60))} minutes`);
        }
      });
    });
  };

  const contextValue = {
    notificationPermission,
    requestPermission,
    showNotification: showNotificationFunc,
    checkAndNotify,
    checkScheduledReminders
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};
