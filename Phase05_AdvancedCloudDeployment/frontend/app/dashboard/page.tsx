'use client';

import { useState, useMemo } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { AnimatedCard, AnimatedPage } from '@/components/ui/animate';
import {
  SearchIcon,
  FilterIcon,
  FlagIcon,
  ArrowUpDownIcon,
  PlusIcon,
  LayoutListIcon,
  LayoutGridIcon,
  RotateCcwIcon,
  XIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Task, Priority, RecurrencePattern } from '@/lib/types';
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask, useToggleTaskCompletion } from '@/hooks/use-tasks';
import { TaskCard } from '@/components/tasks/TaskCard';
import { DeleteConfirmationModal } from '@/components/tasks/DeleteConfirmationModal';
import { ReminderBanner } from '@/components/tasks/ReminderBanner';
import ChatKitWrapper from '@/components/ChatKitWrapper';

export default function DashboardPage() {
  const { data: tasks = [], isLoading } = useTasks();
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const deleteTaskMutation = useDeleteTask();
  const toggleTaskCompletionMutation = useToggleTaskCompletion();

  // Helper to convert local datetime to ISO string without timezone conversion
  const toLocalISOString = (localDateTime: string): string | null => {
    if (!localDateTime || localDateTime.trim() === '') return null;
    // The datetime-local input gives us "YYYY-MM-DDTHH:MM" in local time
    // We just need to append seconds and return it as-is (local time)
    return `${localDateTime}:00`;
  };

  // Helper to convert ISO string to local datetime for editing
  const fromLocalISOString = (isoString: string | null | undefined): string => {
    if (!isoString) return '';
    // Parse the ISO string and convert to local datetime-local format
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'none' as Priority,
    due_date: '',
    tags: '',
    recurrence_pattern: 'none' as RecurrencePattern
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<{ id: string; title: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'todo' | 'completed'>('all');
  const [filterPriority, setFilterPriority] = useState<'all' | Priority>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'priority' | 'due_date' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  // Apply filters and sorting using useMemo
  const filteredTasks = useMemo(() => {
    let result = [...tasks];

    // Apply search filter
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter(task =>
        task.title.toLowerCase().includes(lowerSearch) ||
        (task.description && task.description.toLowerCase().includes(lowerSearch))
      );
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      result = result.filter(task => task.status === filterStatus);
    }

    // Apply priority filter
    if (filterPriority !== 'all') {
      result = result.filter(task => task.priority === filterPriority);
    }

    // Apply sorting
    result.sort((a, b) => {
      let aValue: string | number | Date;
      let bValue: string | number | Date;

      switch (sortBy) {
        case 'priority':
          const priorityOrder: Record<string, number> = {
            'high': 4, 'HIGH': 4,
            'medium': 3, 'MEDIUM': 3,
            'low': 2, 'LOW': 2,
            'none': 1, 'NONE': 1
          };
          aValue = priorityOrder[a.priority] || 0;
          bValue = priorityOrder[b.priority] || 0;
          break;
        case 'due_date':
          aValue = a.due_date ? new Date(a.due_date).getTime() : Infinity;
          bValue = b.due_date ? new Date(b.due_date).getTime() : Infinity;
          break;
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'created_at':
        default:
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return result;
  }, [tasks, searchTerm, filterStatus, filterPriority, sortBy, sortOrder]);

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate: For recurring tasks, due date must be in the future
    if (newTask.due_date && newTask.recurrence_pattern !== 'none') {
      const selectedDate = new Date(newTask.due_date);
      const now = new Date();

      if (selectedDate <= now) {
        toast.error('Invalid Date', {
          description: "You can't add a task for a past date and time. Please select a future date.",
          unstyled: true,
          classNames: {
            toast: 'glass-toast-error font-mono',
            title: 'glass-toast-title font-mono',
            description: 'glass-toast-description font-mono',
          },
        });
        return;
      }
    }

    createTaskMutation.mutate({
      title: newTask.title,
      description: newTask.description,
      priority: newTask.priority,
      due_date: newTask.due_date && newTask.due_date.trim() !== '' ? newTask.due_date : null,
      tags: newTask.tags ? newTask.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
      recurrence_pattern: newTask.recurrence_pattern,
    }, {
      onSuccess: () => closeModal()
    });
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTaskId) return;

    // Validate: For recurring tasks, due date must be in the future
    if (newTask.due_date && newTask.recurrence_pattern !== 'none') {
      const selectedDate = new Date(newTask.due_date);
      const now = new Date();

      if (selectedDate <= now) {
        toast.error('Invalid Date', {
          description: "You can't set a task for a past date and time. Please select a future date.",
          unstyled: true,
          classNames: {
            toast: 'glass-toast-error font-mono',
            title: 'glass-toast-title font-mono',
            description: 'glass-toast-description font-mono',
          },
        });
        return;
      }
    }

    updateTaskMutation.mutate({
      id: editingTaskId,
      data: {
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        due_date: newTask.due_date && newTask.due_date.trim() !== '' ? newTask.due_date : null,
        tags: newTask.tags ? newTask.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
        recurrence_pattern: newTask.recurrence_pattern,
      }
    }, {
      onSuccess: () => closeModal()
    });
  };

  const handleDeleteTask = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      setTaskToDelete({ id: taskId, title: task.title });
      setIsDeleteModalOpen(true);
    }
  };

  const confirmDeleteTask = () => {
    if (taskToDelete) {
      deleteTaskMutation.mutate(taskToDelete.id);
      setIsDeleteModalOpen(false);
      setTaskToDelete(null);
    }
  };

  const cancelDeleteTask = () => {
    setIsDeleteModalOpen(false);
    setTaskToDelete(null);
  };

  const handleToggleTask = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const completed = task.status !== 'completed';
    toggleTaskCompletionMutation.mutate({
      id: taskId,
      completed
    });
  };

  const handleStartEditTask = (task: Task) => {
    setEditingTaskId(task.id);
    setNewTask({
      title: task.title,
      description: task.description ?? '',
      priority: task.priority as Priority,
      due_date: fromLocalISOString(task.due_date),
      tags: task.tags?.join(', ') ?? '',
      recurrence_pattern: task.recurrence_pattern as RecurrencePattern ?? 'none',
    });
    setIsModalOpen(true);
  };

  const openModal = () => {
    setEditingTaskId(null);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingTaskId(null);
    setNewTask({
      title: '',
      description: '',
      priority: 'none',
      due_date: '',
      tags: '',
      recurrence_pattern: 'none'
    });
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setFilterStatus('all');
    setFilterPriority('all');
    setSortBy('created_at');
    setSortOrder('asc');
  };

  // Calculate dashboard statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.status === 'completed').length;
  const pendingTasks = tasks.filter(task => task.status === 'todo' || task.status === '').length;
  const highPriorityTasks = tasks.filter(task => task.priority === 'high' || task.priority === 'HIGH').length;

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 flex flex-col">
      <AnimatedPage className="flex-1">
        <div className="space-y-4 xs:space-y-6 max-w-7xl mx-auto px-2 xs:px-4 sm:px-6 lg:px-8 py-4 xs:py-6 sm:py-8">
          
          {/* Dashboard Header */}
          <AnimatedCard delay={0.1}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 xs:gap-4">
              <div className="min-w-0">
                <h1 className="text-xl xs:text-2xl sm:text-3xl font-extrabold font-mono text-foreground tracking-tight">Dashboard</h1>
                <p className="font-mono text-muted-foreground mt-1 text-xs xs:text-sm sm:text-base lg:text-lg">Manage your tasks with focus and clarity.</p>
              </div>
              <Button
                onClick={openModal}
                className="bg-primary text-primary-foreground hover:bg-primary/90 py-3 px-4 xs:py-4 xs:px-6 sm:py-6 sm:px-8 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-primary/25 font-bold font-mono text-sm xs:text-base sm:text-lg whitespace-nowrap"
              >
                <PlusIcon className="h-4 w-4 xs:h-5 xs:w-5 sm:h-6 sm:w-6 mr-1 xs:mr-2" />
                Add New Task
              </Button>
            </div>
          </AnimatedCard>

          {/* Task Reminder Banner */}
          <ReminderBanner tasks={tasks} />

          {/* Dashboard Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
            <StatCard
              title="Total Tasks"
              value={totalTasks}
              icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />}
              color="primary"
              onClick={() => setFilterStatus('all')}
              delay={0.15}
            />
            <StatCard
              title="Completed"
              value={completedTasks}
              icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />}
              color="success"
              onClick={() => setFilterStatus('completed')}
              delay={0.2}
            />
             <StatCard
              title="Pending"
              value={pendingTasks}
              icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />}
              color="warning"
              onClick={() => setFilterStatus('todo')}
              delay={0.25}
            />
            <StatCard
              title="Urgent"
              value={highPriorityTasks}
              icon={<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />}
              color="danger"
              onClick={() => setFilterPriority('high')}
              delay={0.3}
            />
          </div>

          {/* Controls Bar */}
          <AnimatedCard delay={0.35} className="mt-8">
            <div className="p-4 glass-card rounded-2xl border border-border/40 shadow-xl space-y-6">
              <div className="flex flex-col md:flex-row gap-4 items-center">
                <div className="relative flex-1 w-full">
                  <SearchIcon className="h-5 w-5 text-muted-foreground absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <Input
                    type="text"
                    placeholder="Search tasks by title or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-12 pr-12 bg-background/30 backdrop-blur-sm border-border/50 text-foreground font-mono rounded-xl py-6 w-full focus:ring-2 focus:ring-primary/50 transition-all duration-300 text-lg shadow-inner placeholder:font-mono"
                  />
                  {searchTerm && (
                    <button
                      onClick={() => setSearchTerm('')}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1"
                      aria-label="Clear search"
                    >
                      <XIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
                <Button
                  onClick={handleResetFilters}
                  variant="outline"
                  className="h-12 px-6 rounded-xl border-border/50 hover:bg-accent flex items-center gap-2 font-bold font-mono transition-all"
                  title="Reset all filters"
                >
                  <RotateCcwIcon className="h-4 w-4" />
                  Reset Filters
                </Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                <FilterSelect
                  label="Status"
                  icon={<FilterIcon className="h-4 w-4" />}
                  value={filterStatus}
                  onChange={(v) => setFilterStatus(v as 'all' | 'todo' | 'completed')}
                  options={[
                    { label: 'All Statuses', value: 'all' },
                    { label: 'To Do', value: 'todo' },
                    { label: 'Completed', value: 'completed' }
                  ]}
                />
                <FilterSelect
                  label="Priority"
                  icon={<FlagIcon className="h-4 w-4" />}
                  value={filterPriority}
                  onChange={(v) => setFilterPriority(v as 'all' | Priority)}
                  options={[
                    { label: 'All Priorities', value: 'all' },
                    { label: 'High', value: 'high' },
                    { label: 'Medium', value: 'medium' },
                    { label: 'Low', value: 'low' },
                    { label: 'None', value: 'none' }
                  ]}
                />
                <FilterSelect
                  label="Sort By"
                  icon={<ArrowUpDownIcon className="h-4 w-4" />}
                  value={sortBy}
                  onChange={(v) => setSortBy(v as 'created_at' | 'priority' | 'due_date' | 'title')}
                  options={[
                    { label: 'Created Date', value: 'created_at' },
                    { label: 'Priority Level', value: 'priority' },
                    { label: 'Title Name', value: 'title' },
                    { label: 'Due Date', value: 'due_date' }
                  ]}
                />
                <FilterSelect
                  label="Order"
                  icon={<ArrowUpDownIcon className="h-4 w-4" />}
                  value={sortOrder}
                  onChange={(v) => setSortOrder(v as 'asc' | 'desc')}
                  options={[
                    { label: 'Ascending', value: 'asc' },
                    { label: 'Descending', value: 'desc' }
                  ]}
                />
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-mono font-semibold text-muted-foreground ml-1">View Mode</label>
                  <div className="flex h-10 rounded-lg bg-background/40 backdrop-blur-sm border border-border/50 overflow-hidden shadow-sm">
                    <button
                      onClick={() => setViewMode('list')}
                      className={`flex-1 flex items-center justify-center transition-all duration-300 ${
                        viewMode === 'list' ? 'bg-primary text-primary-foreground shadow-md' : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      }`}
                    >
                      <LayoutListIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`flex-1 flex items-center justify-center transition-all duration-300 ${
                        viewMode === 'grid' ? 'bg-primary text-primary-foreground shadow-md' : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      }`}
                    >
                      <LayoutGridIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </AnimatedCard>

          {/* Task Grid/List */}
          <div className="mt-8">
            <AnimatedCard delay={0.4}>
              <div className="flex items-center justify-between mb-6 px-2">
                <h2 className="text-2xl font-bold font-mono text-foreground">Active Tasks</h2>
                <div className="px-4 py-1.5 rounded-full bg-primary/10 text-primary border border-primary/20 text-sm font-bold font-mono">
                  {filteredTasks.length} Result{filteredTasks.length !== 1 ? 's' : ''}
                </div>
              </div>

              {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[1, 2, 3].map((n) => (
                    <div key={n} className="h-[220px] rounded-xl bg-card/20 animate-pulse border border-border/20" />
                  ))}
                </div>
              ) : filteredTasks.length === 0 ? (
                <div className="text-center py-24 glass-card rounded-2xl border border-dashed border-border/60">
                  <div className="mx-auto w-24 h-24 rounded-full bg-primary/5 flex items-center justify-center mb-6 border border-primary/10">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-primary/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-2">Workspace clear!</h3>
                  <p className="text-muted-foreground mb-8 max-w-sm mx-auto">
                    {searchTerm || filterStatus !== 'all' || filterPriority !== 'all'
                      ? "We couldn't find any tasks matching your filters."
                      : "You've crushed all your tasks. Time to relax or set new goals!"}
                  </p>
                  <Button
                    onClick={openModal}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 py-6 px-10 rounded-xl transition-all font-bold"
                  >
                    Add Task
                  </Button>
                </div>
              ) : (
                <div className={
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                    : 'flex flex-col gap-4'
                }>
                  {filteredTasks.map((task, index) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      index={index}
                      viewMode={viewMode}
                      onToggle={handleToggleTask}
                      onEdit={handleStartEditTask}
                      onDelete={handleDeleteTask}
                    />
                  ))}
                </div>
              )}
            </AnimatedCard>
          </div>
        </div>
      </AnimatedPage>

      {/* Modern Modal Implementation */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-2 xs:p-4 bg-background/80 backdrop-blur-xl animate-in fade-in duration-300">
          <div className="relative w-full max-w-lg bg-card border border-border/50 rounded-2xl xs:rounded-3xl shadow-2xl p-3 xs:p-4 sm:p-6 animate-in zoom-in-95 duration-300">
            <div className="flex justify-between items-center mb-3 xs:mb-4">
              <h2 className="text-base xs:text-lg sm:text-xl font-extrabold text-foreground tracking-tight font-mono">
                {editingTaskId ? 'Refine Task' : 'New Mission'}
              </h2>
              <button
                onClick={closeModal}
                className="p-1.5 rounded-full hover:bg-accent text-muted-foreground transition-colors"
              >
                <PlusIcon className="h-5 w-5 xs:h-6 xs:w-6 rotate-45" />
              </button>
            </div>

            <form onSubmit={editingTaskId ? handleUpdateTask : handleAddTask} className="space-y-2.5 xs:space-y-3 sm:space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Task Title</label>
                <Input
                  type="text"
                  value={newTask.title}
                  onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                  placeholder="What needs to be done?"
                  required
                  className="bg-background/50 border-border/50 rounded-xl py-2 px-3 xs:py-2.5 xs:px-3.5 sm:py-3 sm:px-4 focus:ring-primary shadow-sm text-sm font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Details (Optional)</label>
                <Input
                  type="text"
                  value={newTask.description}
                  onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                  placeholder="Any additional context..."
                  className="bg-background/50 border-border/50 rounded-xl py-2 px-3 xs:py-2.5 xs:px-3.5 sm:py-3 sm:px-4 focus:ring-primary shadow-sm text-sm font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 xs:gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Priority</label>
                  <select
                    value={newTask.priority}
                    onChange={(e) => setNewTask({...newTask, priority: e.target.value as Priority})}
                    className="w-full h-9 xs:h-10 bg-background/50 border border-border/50 rounded-xl px-3 text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all shadow-sm [&>option]:bg-card [&>option]:text-foreground [&>option]:py-2 font-mono"
                  >
                    <option value="none">None</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Recurrence</label>
                  <select
                    value={newTask.recurrence_pattern}
                    onChange={(e) => setNewTask({...newTask, recurrence_pattern: e.target.value as RecurrencePattern})}
                    className="w-full h-9 xs:h-10 bg-background/50 border border-border/50 rounded-xl px-3 text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all shadow-sm [&>option]:bg-card [&>option]:text-foreground [&>option]:py-2 font-mono"
                  >
                    <option value="none">One-time</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Deadline (Optional)</label>
                <input
                  type="datetime-local"
                  value={newTask.due_date}
                  onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                  className="w-full h-9 xs:h-10 bg-background/50 border border-border/50 rounded-xl px-3 text-sm text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all shadow-sm font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-muted-foreground ml-1 font-mono">Tags (Comma separated)</label>
                <Input
                  type="text"
                  value={newTask.tags}
                  onChange={(e) => setNewTask({...newTask, tags: e.target.value})}
                  placeholder="work, life, urgent..."
                  className="bg-background/50 border-border/50 rounded-xl py-2 px-3 xs:py-2.5 xs:px-3.5 sm:py-3 sm:px-4 focus:ring-primary shadow-sm text-sm font-mono placeholder:font-mono"
                />
              </div>

              <div className="flex gap-2 xs:gap-3 pt-2 xs:pt-3">
                <Button
                  type="button"
                  onClick={closeModal}
                  variant="outline"
                  className="flex-1 py-2 xs:py-2.5 sm:py-3 rounded-xl border-border/50 hover:bg-accent transition-all font-bold text-sm font-mono"
                >
                  Discard
                </Button>
                <Button
                  type="submit"
                  disabled={createTaskMutation.isPending || updateTaskMutation.isPending}
                  className="flex-1 py-2 xs:py-2.5 sm:py-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-all font-bold shadow-lg shadow-primary/20 text-sm font-mono"
                >
                  {editingTaskId ? 'Update Details' : 'Initialize Task'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Floating Action Button for Quick Add */}
      <button
        onClick={openModal}
        className="fixed bottom-4 left-4 xs:bottom-6 xs:left-6 sm:bottom-8 sm:left-8 z-40 w-12 h-12 xs:w-14 xs:h-14 sm:w-16 sm:h-16 rounded-full bg-primary text-primary-foreground shadow-2xl hover:shadow-primary/40 flex items-center justify-center transition-all duration-300 transform hover:scale-110 active:scale-95 focus:outline-none focus:ring-4 focus:ring-primary/40"
        aria-label="Quick add task"
      >
        <PlusIcon className="h-6 w-6 xs:h-8 xs:w-8 sm:h-10 sm:w-10" />
      </button>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={isDeleteModalOpen}
        onConfirm={confirmDeleteTask}
        onCancel={cancelDeleteTask}
        taskTitle={taskToDelete?.title}
      />

      {/* AI Chatbot Assistant */}
      <ChatKitWrapper />
    </div>
  );
}

// Sub-components for cleaner structure
function StatCard({ title, value, icon, color, onClick, delay }: {
  title: string; value: number; icon: React.ReactNode; color: 'primary' | 'success' | 'warning' | 'danger'; onClick?: () => void; delay: number;
}) {
  const colorClasses = {
    primary: 'bg-primary/30 text-primary border-primary/20 hover:border-primary/40',
    success: 'bg-success/30 text-success border-success/20 hover:border-success/40',
    warning: 'bg-warning/30 text-warning border-warning/20 hover:border-warning/40',
    danger: 'bg-danger/30 text-danger border-danger/20 hover:border-danger/40',
  };

  return (
    <AnimatedCard delay={delay}>
      <Card
        className={cn(
          "glass-card border-border/40 hover:shadow-2xl transition-all duration-500 overflow-hidden relative group shadow-xl shadow-primary/10 hover:shadow-primary/20 ",
          onClick ? "cursor-pointer active:scale-95" : ""
        )}
        onClick={onClick}
      >
        <div className={cn("absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-500", `bg-${color}`)} />
        <CardContent className="p-3 xs:p-4 sm:p-6 ">
          <div className="flex items-center">
            <div className={cn("p-2 xs:p-3 sm:p-4 rounded-xl xs:rounded-2xl backdrop-blur-md transition-all duration-300 group-hover:scale-110", colorClasses[color])}>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 xs:h-7 xs:w-7 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {icon}
              </svg>
            </div>
            <div className="ml-3 xs:ml-4 sm:ml-5 min-w-0 flex-1">
              <h3 className="text-[10px] xs:text-xs sm:text-sm font-bold font-mono text-muted-foreground uppercase tracking-wider truncate">{title}</h3>
              <p className="text-2xl xs:text-3xl sm:text-4xl font-black font-mono text-foreground mt-0.5 xs:mt-1 tabular-nums">{value}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </AnimatedCard>
  );
}

function FilterSelect({ label, icon, value, onChange, options }: {
  label: string; icon: React.ReactNode; value: string; onChange: (v: string) => void; options: { label: string; value: string }[];
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-semibold font-mono text-muted-foreground ml-1 flex items-center gap-2">
        {icon}
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-10 bg-background/40 backdrop-blur-sm border border-border/50 rounded-lg px-3 text-foreground font-mono focus:ring-2 focus:ring-primary/50 transition-all shadow-sm text-sm [&>option]:bg-card [&>option]:text-foreground [&>option]:py-2"
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}
