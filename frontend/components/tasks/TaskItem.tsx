'use client';

import { useState } from 'react';
import { Task } from '@/lib/types';
import { Check, Trash2, Edit3, Circle } from 'lucide-react';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number, completed: boolean) => Promise<void>;
  onDelete: (taskId: number) => Promise<void>;
  onEdit: (task: Task) => void;
}

export default function TaskItem({ task, onToggleComplete, onDelete, onEdit }: TaskItemProps) {
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setLoading(true);
    try {
      await onToggleComplete(task.id, !task.completed);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      setLoading(true);
      try {
        await onDelete(task.id);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="card card-hover p-5 animate-fadeIn group bg-white dark:bg-gray-800">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <button
          onClick={handleToggle}
          disabled={loading}
          className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
            task.completed
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 border-green-500 shadow-lg shadow-green-500/30'
              : 'border-gray-300 dark:border-gray-600 hover:border-indigo-500 hover:shadow-lg hover:shadow-indigo-500/20'
          } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          {task.completed ? (
            <Check className="w-4 h-4 text-white" />
          ) : (
            <Circle className="w-3 h-3 text-transparent" />
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3 mb-2">
            <h3
              className={`font-semibold text-lg transition-all duration-300 ${
                task.completed
                  ? 'line-through text-gray-400 dark:text-gray-500'
                  : 'text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400'
              }`}
            >
              {task.title}
            </h3>

            {/* Status Badge */}
            {task.completed ? (
              <span className="badge-completed">
                <Check className="w-3 h-3" />
                Completed
              </span>
            ) : (
              <span className="badge-pending">
                <Circle className="w-3 h-3" />
                Pending
              </span>
            )}
          </div>

          {task.description && (
            <p
              className={`text-sm transition-all duration-300 ${
                task.completed
                  ? 'line-through text-gray-400 dark:text-gray-600'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              {task.description}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <button
            onClick={() => onEdit(task)}
            disabled={loading}
            className="p-2 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-all duration-200"
            title="Edit task"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200"
            title="Delete task"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
