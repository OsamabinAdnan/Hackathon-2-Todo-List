import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskApi } from '@/lib/api';
import { TaskCreate, TaskUpdate } from '@/lib/types';
import { toast } from 'sonner';

const toastClassNames = {
  toast: 'glass-toast',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

const toastSuccessClassNames = {
  toast: 'glass-toast-success',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

const toastErrorClassNames = {
  toast: 'glass-toast-error',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

const toastInfoClassNames = {
  toast: 'glass-toast-info',
  title: 'glass-toast-title',
  description: 'glass-toast-description',
};

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => taskApi.fetchTasks(),
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: TaskCreate) => taskApi.createTask(task),
    onSuccess: (newTask) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task Created', {
        description: `"${newTask.title}" has been added to your tasks`,
        duration: 4000,
        unstyled: true,
        classNames: toastSuccessClassNames,
      });
    },
    onError: () => {
      toast.error('Failed to create task', {
        description: 'Please try again',
        unstyled: true,
        classNames: toastErrorClassNames,
      });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TaskUpdate }) =>
      taskApi.updateTask(id, data),
    onSuccess: (updatedTask) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task Updated', {
        description: `"${updatedTask.title}" has been updated`,
        duration: 4000,
        unstyled: true,
        classNames: toastSuccessClassNames,
      });
    },
    onError: () => {
      toast.error('Failed to update task', {
        description: 'Please try again',
        unstyled: true,
        classNames: toastErrorClassNames,
      });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => taskApi.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task Deleted', {
        description: 'Task has been removed',
        duration: 4000,
        unstyled: true,
        classNames: toastSuccessClassNames,
      });
    },
    onError: () => {
      toast.error('Failed to delete task', {
        description: 'Please try again',
        unstyled: true,
        classNames: toastErrorClassNames,
      });
    },
  });
}

export function useToggleTaskCompletion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
      taskApi.toggleTaskCompletion(id, completed),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      if (variables.completed) {
        toast.success('Task Completed', {
          description: 'Great job! Task marked as complete',
          duration: 4000,
          unstyled: true,
          classNames: toastSuccessClassNames,
        });
      } else {
        toast.info('Task Reopened', {
          description: 'Task marked as incomplete',
          duration: 4000,
          unstyled: true,
          classNames: toastInfoClassNames,
        });
      }
    },
    onError: () => {
      toast.error('Failed to update task', {
        description: 'Please try again',
        unstyled: true,
        classNames: toastErrorClassNames,
      });
    },
  });
}
