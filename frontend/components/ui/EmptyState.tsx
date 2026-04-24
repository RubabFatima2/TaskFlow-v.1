'use client';

import { CheckCircle2, Plus } from 'lucide-react';
import Button from './Button';

interface EmptyStateProps {
  onCreateTask: () => void;
}

export default function EmptyState({ onCreateTask }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 animate-fadeIn">
      {/* Illustration */}
      <div className="relative mb-8">
        {/* Glow effect */}
        <div className="absolute inset-0 bg-blue-500/20 blur-3xl rounded-full scale-150" />

        {/* Main circle */}
        <div className="relative w-32 h-32 rounded-full bg-gradient-to-br from-blue-600/20 to-blue-800/20 border-2 border-blue-500/30 flex items-center justify-center">
          <CheckCircle2 className="w-16 h-16 text-blue-400/60" strokeWidth={1.5} />
        </div>

        {/* Floating dots */}
        <div className="absolute -top-2 -right-2 w-4 h-4 rounded-full bg-blue-500/40 animate-float" />
        <div className="absolute -bottom-3 -left-3 w-3 h-3 rounded-full bg-blue-400/30 animate-float" style={{ animationDelay: '0.5s' }} />
        <div className="absolute top-1/2 -right-6 w-2 h-2 rounded-full bg-blue-300/40 animate-float" style={{ animationDelay: '1s' }} />
      </div>

      {/* Text content */}
      <h3 className="text-2xl font-bold text-white mb-2 font-display">
        No tasks yet
      </h3>
      <p className="text-gray-400 text-center max-w-md mb-8 font-body">
        Start organizing your work by creating your first task. Stay productive and track your progress effortlessly.
      </p>

      {/* CTA Button */}
      <Button
        onClick={onCreateTask}
        size="lg"
        className="btn btn-gradient-primary px-8 py-3 text-base font-semibold gap-2 shadow-lg hover:shadow-blue-500/50"
      >
        <Plus className="w-5 h-5" />
        Create Your First Task
      </Button>

      {/* Subtle hint */}
      <p className="text-gray-500 text-sm mt-6 font-body">
        Tip: Use keyboard shortcuts to work faster
      </p>
    </div>
  );
}
