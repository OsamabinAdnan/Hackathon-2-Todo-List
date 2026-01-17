import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import DashboardPage from '@/app/dashboard/page';

const mockFetch = vi.fn();

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('DashboardPage task CRUD', () => {
  beforeEach(() => {
    mockFetch.mockReset();
    // @ts-expect-error - override fetch for tests
    global.fetch = mockFetch;

    // Mock localStorage token presence
    const tokenPayload = { sub: 'user-123' };
    const base64 = btoa(JSON.stringify(tokenPayload));
    const token = `x.${base64}.y`;

    const localStorageMock = {
      getItem: vi.fn((key: string) => (key === 'token' ? token : null)),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };

    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });

    // Avoid actually navigating
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    });
  });

  it('renders tasks returned as a raw array (fix for reload disappearing tasks)', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          id: 'task-1',
          title: 'Task From API',
          description: 'desc',
          status: 'todo',
          priority: 'none',
          due_date: null,
          recurrence_pattern: 'none',
          tags: [],
          created_at: new Date().toISOString(),
          completed_at: null,
        },
      ],
    });

    render(
      <QueryClientProvider client={createTestQueryClient()}>
        <DashboardPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Task From API')).toBeInTheDocument();
    });
  });

  it('deletes a task from UI after successful DELETE', async () => {
    // Initial fetchTasks
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          id: 'task-1',
          title: 'Delete Me',
          description: null,
          status: 'todo',
          priority: 'none',
          due_date: null,
          recurrence_pattern: 'none',
          tags: [],
          created_at: new Date().toISOString(),
          completed_at: null,
        },
      ],
    });

    // DELETE call
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: async () => ({}),
    });

    // Re-fetch after mutation
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(
      <QueryClientProvider client={createTestQueryClient()}>
        <DashboardPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Delete Me')).toBeInTheDocument();
    });

    const user = userEvent.setup();

    // Mock confirm dialog
    vi.spyOn(window, 'confirm').mockImplementation(() => true);

    const deleteButtons = await screen.findAllByLabelText('Delete Task');
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('Delete Me')).not.toBeInTheDocument();
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/tasks/task-1'),
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  it('opens edit modal when clicking edit button', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          id: 'task-1',
          title: 'Editable',
          description: 'hello',
          status: 'todo',
          priority: 'none',
          due_date: null,
          recurrence_pattern: 'none',
          tags: ['tag1'],
          created_at: new Date().toISOString(),
          completed_at: null,
        },
      ],
    });

    render(
      <QueryClientProvider client={createTestQueryClient()}>
        <DashboardPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Editable')).toBeInTheDocument();
    });

    const user = userEvent.setup();
    const editButtons = await screen.findAllByLabelText('Edit Task');
    await user.click(editButtons[0]);

    expect(screen.getByText('Refine Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Editable')).toBeInTheDocument();
  });
});
