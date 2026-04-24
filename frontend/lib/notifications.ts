// Request notification permission
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!('Notification' in window)) {
    console.warn('This browser does not support notifications');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  return false;
};

// Show a notification
export const showNotification = (title: string, options?: NotificationOptions) => {
  if (Notification.permission === 'granted') {
    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options,
    });
  }
};

// Check if a task reminder should be shown
export const checkTaskReminders = (tasks: any[]) => {
  const now = new Date();

  tasks.forEach((task) => {
    if (
      !task.completed &&
      task.reminder_enabled &&
      task.due_date &&
      task.reminder_minutes_before
    ) {
      const dueDate = new Date(task.due_date);
      const reminderTime = new Date(dueDate.getTime() - task.reminder_minutes_before * 60000);

      // Check if we should show the reminder (within 1 minute window)
      const timeDiff = reminderTime.getTime() - now.getTime();
      if (timeDiff > 0 && timeDiff <= 60000) {
        showNotification(`Task Reminder: ${task.title}`, {
          body: task.description || 'Your task is due soon!',
          tag: `task-${task.id}`,
          requireInteraction: true,
        });
      }
    }
  });
};

// Schedule recurring task
export const getNextRecurrenceDate = (
  currentDate: Date,
  pattern: string,
  interval: number
): Date => {
  const nextDate = new Date(currentDate);

  switch (pattern) {
    case 'daily':
      nextDate.setDate(nextDate.getDate() + interval);
      break;
    case 'weekly':
      nextDate.setDate(nextDate.getDate() + interval * 7);
      break;
    case 'monthly':
      nextDate.setMonth(nextDate.getMonth() + interval);
      break;
    case 'yearly':
      nextDate.setFullYear(nextDate.getFullYear() + interval);
      break;
  }

  return nextDate;
};

// Check if notification permission is granted
export const hasNotificationPermission = (): boolean => {
  return 'Notification' in window && Notification.permission === 'granted';
};
