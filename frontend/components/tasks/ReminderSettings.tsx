import { Bell } from 'lucide-react';

interface ReminderSettingsProps {
  reminderEnabled: boolean;
  reminderMinutesBefore: number;
  onReminderEnabledChange: (enabled: boolean) => void;
  onReminderMinutesChange: (minutes: number) => void;
}

export default function ReminderSettings({
  reminderEnabled,
  reminderMinutesBefore,
  onReminderEnabledChange,
  onReminderMinutesChange,
}: ReminderSettingsProps) {
  const reminderOptions = [
    { label: '5 minutes before', value: 5 },
    { label: '15 minutes before', value: 15 },
    { label: '30 minutes before', value: 30 },
    { label: '1 hour before', value: 60 },
    { label: '2 hours before', value: 120 },
    { label: '1 day before', value: 1440 },
  ];

  return (
    <div className="space-y-4">
      {/* Enable Reminder Toggle */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="reminder"
          checked={reminderEnabled}
          onChange={(e) => onReminderEnabledChange(e.target.checked)}
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
        />
        <label htmlFor="reminder" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
          <Bell className="w-4 h-4" />
          Set a reminder
        </label>
      </div>

      {/* Reminder Options */}
      {reminderEnabled && (
        <div className="pl-7 animate-fadeIn">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Remind me
          </label>
          <select
            value={reminderMinutesBefore}
            onChange={(e) => onReminderMinutesChange(parseInt(e.target.value))}
            className="input"
          >
            {reminderOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            You'll receive a browser notification before the task is due
          </p>
        </div>
      )}
    </div>
  );
}
