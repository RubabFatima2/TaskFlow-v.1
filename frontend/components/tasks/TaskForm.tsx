'use client';

import { useState, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { Task, Priority, RecurrencePattern } from '@/lib/types';
import { Save, X, Plus, Tag as TagIcon } from 'lucide-react';
import Tag from '@/components/ui/Tag';
import RecurringTaskSettings from '@/components/tasks/RecurringTaskSettings';
import ReminderSettings from '@/components/tasks/ReminderSettings';

interface TaskFormProps {
  onSubmit: (
    title: string,
    description?: string,
    priority?: Priority,
    tags?: string[],
    dueDate?: string,
    isRecurring?: boolean,
    recurrencePattern?: RecurrencePattern | null,
    recurrenceInterval?: number,
    recurrenceEndDate?: string,
    reminderEnabled?: boolean,
    reminderMinutesBefore?: number
  ) => Promise<void>;
  initialTask?: Task;
  onCancel?: () => void;
}

export default function TaskForm({ onSubmit, initialTask, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title || '');
  const [description, setDescription] = useState(initialTask?.description || '');
  const [priority, setPriority] = useState<Priority>(initialTask?.priority || 'medium');
  const [tags, setTags] = useState<string[]>(initialTask?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [dueDate, setDueDate] = useState(initialTask?.due_date || '');
  const [isRecurring, setIsRecurring] = useState(initialTask?.is_recurring || false);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern | null>(
    initialTask?.recurrence_pattern || null
  );
  const [recurrenceInterval, setRecurrenceInterval] = useState(initialTask?.recurrence_interval || 1);
  const [recurrenceEndDate, setRecurrenceEndDate] = useState(initialTask?.recurrence_end_date || '');
  const [reminderEnabled, setReminderEnabled] = useState(initialTask?.reminder_enabled || false);
  const [reminderMinutesBefore, setReminderMinutesBefore] = useState(
    initialTask?.reminder_minutes_before || 15
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title);
      setDescription(initialTask.description || '');
      setPriority(initialTask.priority || 'medium');
      setTags(initialTask.tags || []);
      setDueDate(initialTask.due_date || '');
      setIsRecurring(initialTask.is_recurring || false);
      setRecurrencePattern(initialTask.recurrence_pattern || null);
      setRecurrenceInterval(initialTask.recurrence_interval || 1);
      setRecurrenceEndDate(initialTask.recurrence_end_date || '');
      setReminderEnabled(initialTask.reminder_enabled || false);
      setReminderMinutesBefore(initialTask.reminder_minutes_before || 15);
    }
  }, [initialTask]);

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (isRecurring && !recurrencePattern) {
      setError('Please select a recurrence pattern');
      return;
    }

    setLoading(true);
    try {
      await onSubmit(
        title.trim(),
        description.trim() || undefined,
        priority,
        tags,
        dueDate || undefined,
        isRecurring,
        recurrencePattern,
        recurrenceInterval,
        recurrenceEndDate || undefined,
        reminderEnabled,
        reminderMinutesBefore
      );
      if (!initialTask) {
        setTitle('');
        setDescription('');
        setPriority('medium');
        setTags([]);
        setDueDate('');
        setIsRecurring(false);
        setRecurrencePattern(null);
        setRecurrenceInterval(1);
        setRecurrenceEndDate('');
        setReminderEnabled(false);
        setReminderMinutesBefore(15);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 max-h-[70vh] overflow-y-auto custom-scrollbar pr-2">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter task title"
        required
        maxLength={200}
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Description (optional)
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description"
          maxLength={10000}
          rows={4}
          className="input resize-none custom-scrollbar"
        />
      </div>

      {/* Priority Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Priority
        </label>
        <div className="flex gap-3">
          {(['low', 'medium', 'high'] as Priority[]).map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPriority(p)}
              className={`flex-1 px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                priority === p
                  ? p === 'high'
                    ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-300 dark:border-red-800/50'
                    : p === 'medium'
                    ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-300 dark:border-amber-800/50'
                    : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-300 dark:border-blue-800/50'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Tags (optional)
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddTag();
              }
            }}
            placeholder="Add a tag"
            className="input flex-1"
          />
          <Button
            type="button"
            onClick={handleAddTag}
            variant="secondary"
            size="md"
            disabled={!tagInput.trim()}
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <Tag key={tag} label={tag} onRemove={() => handleRemoveTag(tag)} />
            ))}
          </div>
        )}
      </div>

      {/* Due Date & Time */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Due Date & Time (optional)
        </label>
        <input
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="input"
          min={new Date().toISOString().slice(0, 16)}
        />
      </div>

      {/* Recurring Task Settings */}
      <RecurringTaskSettings
        isRecurring={isRecurring}
        recurrencePattern={recurrencePattern}
        recurrenceInterval={recurrenceInterval}
        recurrenceEndDate={recurrenceEndDate}
        onRecurringChange={setIsRecurring}
        onPatternChange={setRecurrencePattern}
        onIntervalChange={setRecurrenceInterval}
        onEndDateChange={setRecurrenceEndDate}
      />

      {/* Reminder Settings */}
      {dueDate && (
        <ReminderSettings
          reminderEnabled={reminderEnabled}
          reminderMinutesBefore={reminderMinutesBefore}
          onReminderEnabledChange={setReminderEnabled}
          onReminderMinutesChange={setReminderMinutesBefore}
        />
      )}

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm animate-slideIn">
          {error}
        </div>
      )}

      <div className="flex gap-3 pt-2 sticky bottom-0 bg-white dark:bg-gray-800 pb-2">
        <Button type="submit" disabled={loading} className="flex-1 btn-gradient-primary" size="lg">
          <Save className="w-4 h-4" />
          {loading ? 'Saving...' : initialTask ? 'Update Task' : 'Create Task'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} size="lg">
            <X className="w-4 h-4" />
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
