import { RecurrencePattern } from '@/lib/types';
import { Repeat, Calendar } from 'lucide-react';

interface RecurringTaskSettingsProps {
  isRecurring: boolean;
  recurrencePattern: RecurrencePattern | null;
  recurrenceInterval: number;
  recurrenceEndDate: string;
  onRecurringChange: (isRecurring: boolean) => void;
  onPatternChange: (pattern: RecurrencePattern) => void;
  onIntervalChange: (interval: number) => void;
  onEndDateChange: (date: string) => void;
}

export default function RecurringTaskSettings({
  isRecurring,
  recurrencePattern,
  recurrenceInterval,
  recurrenceEndDate,
  onRecurringChange,
  onPatternChange,
  onIntervalChange,
  onEndDateChange,
}: RecurringTaskSettingsProps) {
  return (
    <div className="space-y-4">
      {/* Enable Recurring Toggle */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="recurring"
          checked={isRecurring}
          onChange={(e) => onRecurringChange(e.target.checked)}
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
        />
        <label htmlFor="recurring" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
          <Repeat className="w-4 h-4" />
          Make this a recurring task
        </label>
      </div>

      {/* Recurring Options */}
      {isRecurring && (
        <div className="pl-7 space-y-4 animate-fadeIn">
          {/* Pattern Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Repeat Pattern
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(['daily', 'weekly', 'monthly', 'yearly'] as RecurrencePattern[]).map((pattern) => (
                <button
                  key={pattern}
                  type="button"
                  onClick={() => onPatternChange(pattern)}
                  className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                    recurrencePattern === pattern
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-300 dark:border-blue-800/50'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  {pattern.charAt(0).toUpperCase() + pattern.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Repeat Every
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={recurrenceInterval}
                onChange={(e) => onIntervalChange(parseInt(e.target.value) || 1)}
                className="input w-20"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {recurrencePattern === 'daily' && 'day(s)'}
                {recurrencePattern === 'weekly' && 'week(s)'}
                {recurrencePattern === 'monthly' && 'month(s)'}
                {recurrencePattern === 'yearly' && 'year(s)'}
              </span>
            </div>
          </div>

          {/* End Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              End Date (optional)
            </label>
            <input
              type="date"
              value={recurrenceEndDate}
              onChange={(e) => onEndDateChange(e.target.value)}
              className="input"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>
      )}
    </div>
  );
}
