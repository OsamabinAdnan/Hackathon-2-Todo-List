import { Task, TaskCreate, TaskUpdate, User, UserUpdate, ChangePasswordRequest } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getUserIdFromToken = (token: string): string => {
  try {
    if (!token || typeof token !== 'string') {
      throw new Error('Token is missing or invalid');
    }

    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Token format is invalid (expected 3 parts)');
    }

    const base64Url = parts[1];
    if (!base64Url) {
      throw new Error('Token payload is missing');
    }

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const tokenPayload = JSON.parse(atob(base64)) as { sub?: string; user_id?: string; id?: string };

    // Check various common subject/user_id claims
    const userId = tokenPayload.sub || tokenPayload.user_id || tokenPayload.id;

    if (!userId) {
      throw new Error('Token missing sub/user_id claim');
    }
    return userId;
  } catch (e) {
    console.error('Error decoding token:', e);
    // Clear invalid token from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    throw new Error('Invalid token - please log in again');
  }
};

const getAuthHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
};

export const getUserId = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (!token) throw new Error('No authentication token found');
    return getUserIdFromToken(token);
};

export const taskApi = {
  fetchTasks: async (): Promise<Task[]> => {
    const userId = getUserId();
    const response = await fetch(`${API_URL}/api/${userId}/tasks`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
          if (typeof window !== 'undefined') window.location.href = '/login';
      }
      throw new Error('Failed to fetch tasks');
    }

    const data: unknown = await response.json();
    return Array.isArray(data)
      ? (data as Task[])
      : (data as { tasks?: Task[] }).tasks ?? [];
  },

  createTask: async (task: TaskCreate): Promise<Task> => {
    const userId = getUserId();
    const response = await fetch(`${API_URL}/api/${userId}/tasks`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(task),
    });

    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  },

  updateTask: async (taskId: string, task: TaskUpdate): Promise<Task> => {
    const userId = getUserId();
    const response = await fetch(`${API_URL}/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(task),
    });

    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  },

  deleteTask: async (taskId: string): Promise<void> => {
    const userId = getUserId();
    const response = await fetch(`${API_URL}/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) throw new Error('Failed to delete task');
  },

  toggleTaskCompletion: async (taskId: string, completed: boolean): Promise<Task> => {
    const userId = getUserId();
    const response = await fetch(`${API_URL}/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ completed }),
    });

    if (!response.ok) throw new Error('Failed to toggle task completion');
    return response.json();
  },
};

export const userApi = {
  updateProfile: async (userUpdate: UserUpdate): Promise<User> => {
    const response = await fetch(`${API_URL}/api/users/profile`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(userUpdate),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update profile');
    }
    return response.json();
  },

  changePassword: async (passwordData: ChangePasswordRequest): Promise<{ message: string }> => {
    const response = await fetch(`${API_URL}/api/users/change-password`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(passwordData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to change password');
    }
    return response.json();
  },

  deleteAccount: async (): Promise<{ message: string }> => {
    const response = await fetch(`${API_URL}/api/users/account`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete account');
    }
    return response.json();
  },
};
