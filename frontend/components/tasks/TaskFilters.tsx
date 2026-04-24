'use client';

import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface TaskFiltersProps {
  activeFilter: 'all' | 'completed' | 'pending';
  onFilterChange: (filter: 'all' | 'completed' | 'pending') => void;
  counts: {
    all: number;
    completed: number;
    pending: number;
  };
}

export default function TaskFilters({ activeFilter, onFilterChange, counts }: TaskFiltersProps) {
  const filters = [
    {
      id: 'all' as const,
      label: 'All Tasks',
      icon: AlertCircle,
      count: counts.all,
      color: 'indigo',
    },
    {
      id: 'completed' as const,
      label: 'Completed',
      icon: CheckCircle,
      count: counts.completed,
      color: 'green',
    },
    {
      id: 'pending' as const,
      label: 'Pending',
      icon: Clock,
      count: counts.pending,
      color: 'yellow',
    },
  ];

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {filters.map((filter) => {
        const Icon = filter.icon;
        const isActive = activeFilter === filter.id;

        return (
          <button
            key={filter.id}
            onClick={() => onFilterChange(filter.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 whitespace-nowrap ${
              isActive
                ? filter.color === 'indigo'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg glow-indigo'
                  : filter.color === 'green'
                  ? 'bg-green-500 text-white shadow-lg'
                  : 'bg-yellow-500 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-500'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{filter.label}</span>
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                isActive
                  ? 'bg-white/20'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
            >
              {filter.count}
            </span>
          </button>
        );
      })}
    </div>
  );
}
