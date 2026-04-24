import { X } from 'lucide-react';

interface TagProps {
  label: string;
  onRemove?: () => void;
  size?: 'sm' | 'md';
}

export default function Tag({ label, onRemove, size = 'md' }: TagProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium border ${sizeClasses} bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800/30`}
    >
      {label}
      {onRemove && (
        <button
          onClick={onRemove}
          className="hover:bg-blue-200 dark:hover:bg-blue-800/40 rounded-full p-0.5 transition-colors"
          aria-label={`Remove ${label} tag`}
        >
          <X className={iconSize} />
        </button>
      )}
    </span>
  );
}
