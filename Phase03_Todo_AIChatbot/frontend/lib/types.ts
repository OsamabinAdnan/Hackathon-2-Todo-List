export type Priority = 'high' | 'medium' | 'low' | 'none' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Task {
  id: string;
  user_id?: string;
  title: string;
  description?: string | null;
  status: string;
  priority: Priority;
  due_date?: string | null;
  recurrence_pattern?: RecurrencePattern | null;
  tags: string[];
  created_at: string;
  updated_at?: string;
  completed_at?: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority: Priority;
  due_date?: string | null;
  tags: string[];
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskUpdate extends Partial<TaskCreate> {
  status?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface UserUpdate {
  name?: string;
  email?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
