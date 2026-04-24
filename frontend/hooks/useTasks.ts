'use client';

import { useState, useEffect } from 'react';
import { Task } from '@/lib/types';
import { apiClient } from '@/lib/api-client';

export default function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Cleanup function to handle component unmount
    return () => {
      // Any pending requests will be handled by the component
    };
  }, []);

  const fetchTasks = async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<{ tasks: Task[]; total: number }>('/api/v1/tasks', { signal });
      setTasks(response.tasks);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'Failed to fetch tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (
    title: string,
    description?: string,
    priority?: string,
    tags?: string[],
    dueDate?: string,
    isRecurring?: boolean,
    recurrencePattern?: string | null,
    recurrenceInterval?: number,
    recurrenceEndDate?: string,
    reminderEnabled?: boolean,
    reminderMinutesBefore?: number
  ) => {
    setError(null);
    try {
      const newTask = await apiClient.post<Task>('/api/v1/tasks', {
        title,
        description: description || null,
        priority: priority || 'medium',
        tags: tags || [],
        due_date: dueDate || null,
        is_recurring: isRecurring || false,
        recurrence_pattern: recurrencePattern || null,
        recurrence_interval: recurrenceInterval || 1,
        recurrence_end_date: recurrenceEndDate || null,
        reminder_enabled: reminderEnabled || false,
        reminder_minutes_before: reminderMinutesBefore || null,
      });
      setTasks([newTask, ...tasks]);
      return newTask;
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
      throw err;
    }
  };

  const updateTask = async (taskId: number, updates: Partial<Task>) => {
    setError(null);
    try {
      console.log('Updating task:', taskId, 'with updates:', updates);
      const updatedTask = await apiClient.put<Task>(`/api/v1/tasks/${taskId}`, updates);
      console.log('Update successful:', updatedTask);
      setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
      return updatedTask;
    } catch (err: any) {
      console.error('Update failed:', err);
      setError(err.message || 'Failed to update task');
      throw err;
    }
  };

  const toggleTaskCompleted = async (taskId: number, completed: boolean) => {
    return updateTask(taskId, { completed });
  };

  const deleteTask = async (taskId: number) => {
    setError(null);
    try {
      await apiClient.delete(`/api/v1/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
      throw err;
    }
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleTaskCompleted,
    deleteTask,
  };
}
