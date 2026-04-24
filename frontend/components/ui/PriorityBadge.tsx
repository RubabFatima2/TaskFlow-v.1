import { Priority } from '@/lib/types';
import { AlertCircle, ArrowUp, Minus } from 'lucide-react';

interface PriorityBadgeProps {
  priority: Priority;
  size?: 'sm' | 'md';
}

export default function PriorityBadge({ priority, size = 'md' }: PriorityBadgeProps) {
  const config = {
    high: {
      label: 'High',
      icon: AlertCircle,
      bgLight: 'bg-red-50',
      bgDark: 'dark:bg-red-900/20',
      textLight: 'text-red-700',
      textDark: 'dark:text-red-400',
      borderLight: 'border-red-200',
      borderDark: 'dark:border-red-800/30',
    },
    medium: {
      label: 'Medium',
      icon: ArrowUp,
      bgLight: 'bg-amber-50',
      bgDark: 'dark:bg-amber-900/20',
      textLight: 'text-amber-700',
      textDark: 'dark:text-amber-400',
      borderLight: 'border-amber-200',
      borderDark: 'dark:border-amber-800/30',
    },
    low: {
      label: 'Low',
      icon: Minus,
      bgLight: 'bg-blue-50',
      bgDark: 'dark:bg-blue-900/20',
      textLight: 'text-blue-700',
      textDark: 'dark:text-blue-400',
      borderLight: 'border-blue-200',
      borderDark: 'dark:border-blue-800/30',
    },
  };

  const { label, icon: Icon, bgLight, bgDark, textLight, textDark, borderLight, borderDark } = config[priority];
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-semibold border ${sizeClasses} ${bgLight} ${bgDark} ${textLight} ${textDark} ${borderLight} ${borderDark}`}
    >
      <Icon className={iconSize} />
      {label}
    </span>
  );
}
