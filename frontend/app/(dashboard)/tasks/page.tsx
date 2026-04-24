// 'use client';

// import { useEffect, useState } from 'react';
// import { useAuth } from '@/context/AuthContext';
// import { useRouter } from 'next/navigation';
// import useTasks from '@/hooks/useTasks';
// import TaskList from '@/components/tasks/TaskList';
// import TaskForm from '@/components/tasks/TaskForm';
// import TaskFilters from '@/components/tasks/TaskFilters';
// import Modal from '@/components/ui/Modal';
// import Button from '@/components/ui/Button';
// import Sidebar from '@/components/layout/Sidebar';
// import TopNavbar from '@/components/layout/TopNavbar';
// import { Task } from '@/lib/types';
// import { Plus, Loader2 } from 'lucide-react';

// export default function TasksPage() {
//   const { user, logout } = useAuth();
//   const router = useRouter();
//   const { tasks, loading, error, fetchTasks, createTask, updateTask, toggleTaskCompleted, deleteTask } = useTasks();
//   const [showCreateModal, setShowCreateModal] = useState(false);
//   const [editingTask, setEditingTask] = useState<Task | null>(null);
//   const [activeFilter, setActiveFilter] = useState<'all' | 'completed' | 'pending'>('all');

//   useEffect(() => {
//     const abortController = new AbortController();
//     fetchTasks(abortController.signal);

//     return () => {
//       abortController.abort();
//     };
//   }, []);

//   const handleLogout = async () => {
//     await logout();
//     router.push('/');
//   };

//   const handleCreateTask = async (title: string, description?: string) => {
//     await createTask(title, description);
//     setShowCreateModal(false);
//   };

//   const handleUpdateTask = async (title: string, description?: string) => {
//     if (editingTask) {
//       await updateTask(editingTask.id, { title, description });
//       setEditingTask(null);
//     }
//   };

//   const handleEdit = (task: Task) => {
//     setEditingTask(task);
//   };


//   const filteredTasks = tasks.filter(task => {
//     if (activeFilter === 'completed') return task.completed;
//     if (activeFilter === 'pending') return !task.completed;
//     return true;
//   });

//   const completedCount = tasks.filter(t => t.completed).length;
//   const pendingCount = tasks.filter(t => !t.completed).length;

//   return (
//     <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
//       {/* Sidebar */}
//       <Sidebar onLogout={handleLogout} />

//       {/* Main Content */}
//       <div className="flex-1 flex flex-col overflow-hidden">
//         {/* Top Navbar */}
//         <TopNavbar user={user || undefined} />

//         {/* Page Content */}
//         <main className="flex-1 overflow-y-auto custom-scrollbar">
//           <div className="max-w-7xl mx-auto px-6 py-8">
//             {/* Header */}
//             <div className="mb-8">
//               <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
//                 Task Management
//               </h1>
//               <p className="text-gray-600 dark:text-gray-400">
//                 Organize and track your tasks efficiently
//               </p>
//             </div>

//             {/* Filters & Add Button */}
//             <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
//               <TaskFilters
//                 activeFilter={activeFilter}
//                 onFilterChange={setActiveFilter}
//                 counts={{
//                   all: tasks.length,
//                   completed: completedCount,
//                   pending: pendingCount,
//                 }}
//               />
//               <Button onClick={() => setShowCreateModal(true)} size="lg" className="btn-gradient-primary">
//                 <Plus className="w-5 h-5" />
//                 Add Task
//               </Button>
//             </div>

//             {/* Error Message */}
//             {error && (
//               <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 animate-slideIn">
//                 {error}
//               </div>
//             )}

//             {/* Tasks List */}
//             {loading && tasks.length === 0 ? (
//               <div className="flex flex-col items-center justify-center py-20">
//                 <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mb-4" />
//                 <p className="text-gray-500 dark:text-gray-400">Loading tasks...</p>
//               </div>
//             ) : (
//               <TaskList
//                 tasks={filteredTasks}
//                 onToggleComplete={toggleTaskCompleted}
//                 onDelete={deleteTask}
//                 onEdit={handleEdit}
//               />
//             )}
//           </div>
//         </main>
//       </div>

//       {/* Create Modal */}
//       <Modal
//         isOpen={showCreateModal}
//         onClose={() => setShowCreateModal(false)}
//         title="Create New Task"
//       >
//         <TaskForm
//           onSubmit={handleCreateTask}
//           onCancel={() => setShowCreateModal(false)}
//         />
//       </Modal>

//       {/* Edit Modal */}
//       <Modal
//         isOpen={!!editingTask}
//         onClose={() => setEditingTask(null)}
//         title="Edit Task"
//       >
//         {editingTask && (
//           <TaskForm
//             onSubmit={handleUpdateTask}
//             initialTask={editingTask}
//             onCancel={() => setEditingTask(null)}
//           />
//         )}
//       </Modal>
//     </div>
//   );
// }
'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import useTasks from '@/hooks/useTasks';
import TaskList from '@/components/tasks/TaskList';
import TaskForm from '@/components/tasks/TaskForm';
import TaskFilters from '@/components/tasks/TaskFilters';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Sidebar from '@/components/layout/Sidebar';
import TopNavbar from '@/components/layout/TopNavbar';
import { Task, Priority, RecurrencePattern } from '@/lib/types';
import { Plus, Loader2, CheckCircle2, Clock, LayoutList, AlertCircle, Search } from 'lucide-react';
import EmptyState from '@/components/ui/EmptyState';
import Confetti from '@/components/ui/Confetti';
import TaskSort, { SortOption } from '@/components/tasks/TaskSort';
import { requestNotificationPermission, checkTaskReminders } from '@/lib/notifications';

export default function TasksPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const { tasks, loading, error, fetchTasks, createTask, updateTask, toggleTaskCompleted, deleteTask } = useTasks();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [activeFilter, setActiveFilter] = useState<'all' | 'completed' | 'pending'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showConfetti, setShowConfetti] = useState(false);
  const [sortBy, setSortBy] = useState<SortOption>('date');

  useEffect(() => {
    const abortController = new AbortController();
    fetchTasks(abortController.signal);

    return () => {
      abortController.abort();
    };
  }, []);

  // Separate effect for notifications to avoid re-fetching tasks
  useEffect(() => {
    // Request notification permission once
    requestNotificationPermission();

    // Check for task reminders every minute
    const reminderInterval = setInterval(() => {
      if (tasks.length > 0) {
        checkTaskReminders(tasks);
      }
    }, 60000); // Check every minute

    return () => {
      clearInterval(reminderInterval);
    };
  }, [tasks]);

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  const handleCreateTask = async (
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
  ) => {
    await createTask(
      title,
      description,
      priority,
      tags,
      dueDate,
      isRecurring,
      recurrencePattern,
      recurrenceInterval,
      recurrenceEndDate,
      reminderEnabled,
      reminderMinutesBefore
    );
    setShowCreateModal(false);
  };

  const handleUpdateTask = async (
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
  ) => {
    if (editingTask) {
      await updateTask(editingTask.id, {
        title,
        description,
        priority,
        tags,
        due_date: dueDate,
        is_recurring: isRecurring,
        recurrence_pattern: recurrencePattern,
        recurrence_interval: recurrenceInterval,
        recurrence_end_date: recurrenceEndDate,
        reminder_enabled: reminderEnabled,
        reminder_minutes_before: reminderMinutesBefore,
      });
      setEditingTask(null);
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
  };

  const handleToggleComplete = async (taskId: number, completed: boolean) => {
    await toggleTaskCompleted(taskId, completed);
    // Show confetti when task is completed
    if (completed) {
      setShowConfetti(true);
    }
  };

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    // Ensure task has required fields
    if (!task || !task.title) return false;

    // Status filter
    if (activeFilter === 'completed' && !task.completed) return false;
    if (activeFilter === 'pending' && task.completed) return false;

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchesTitle = task.title.toLowerCase().includes(query);
      const matchesDescription = task.description?.toLowerCase().includes(query);
      return matchesTitle || matchesDescription;
    }

    return true;
  });

  // Sort tasks
  const sortedTasks = [...filteredTasks].sort((a, b) => {
    try {
      if (sortBy === 'priority') {
        const priorityOrder: Record<string, number> = { high: 3, medium: 2, low: 1 };
        const aPriority = priorityOrder[a.priority || 'medium'] || 2;
        const bPriority = priorityOrder[b.priority || 'medium'] || 2;
        return bPriority - aPriority;
      } else if (sortBy === 'date') {
        // Sort by due date (tasks with no due date go to the end)
        if (!a.due_date && !b.due_date) return 0;
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      } else if (sortBy === 'alphabetical') {
        return (a.title || '').localeCompare(b.title || '');
      }
      return 0;
    } catch (error) {
      console.error('Error sorting tasks:', error, { a, b, sortBy });
      return 0;
    }
  });

  console.log('Active filter:', activeFilter);
  console.log('Search query:', searchQuery);
  console.log('Sort by:', sortBy);
  console.log('Total tasks:', tasks.length);
  console.log('Filtered tasks:', filteredTasks.length);
  console.log('Sorted tasks:', sortedTasks.length);
  console.log('Sample task:', tasks[0]);

  const completedCount = tasks.filter(t => t.completed).length;
  const pendingCount = tasks.filter(t => !t.completed).length;
  const completionPercent = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  return (
    <div className="flex h-screen overflow-hidden bg-[hsl(var(--background))]">

      {/* ── Sidebar ── */}
      <Sidebar onLogout={handleLogout} />

      {/* ── Main Content ── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* ── Top Navbar ── */}
        <TopNavbar user={user || undefined} />

        {/* ── Page Content ── */}
        <main className="flex-1 overflow-y-auto overflow-x-visible custom-scrollbar">
          <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 overflow-visible">

            {/* ── Hero Header ── */}
            <div className="page-header animate-fadeIn">
              {/* Decorative orbs */}
              <div
                className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-20 pointer-events-none"
                style={{
                  background: 'radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%)',
                  transform: 'translate(30%, -30%)',
                }}
              />
              <div
                className="absolute bottom-0 left-1/3 w-40 h-40 rounded-full opacity-10 pointer-events-none"
                style={{
                  background: 'radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%)',
                  transform: 'translateY(50%)',
                }}
              />

              <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div>
                  <p className="text-white/70 text-sm font-medium tracking-widest uppercase mb-2 font-body">
                    Workspace
                  </p>
                  <h1 className="text-3xl sm:text-4xl font-bold text-white font-display leading-tight">
                    Task Management
                  </h1>
                  <p className="text-white/75 mt-2 text-base font-body">
                    Organize and track your tasks efficiently
                  </p>
                </div>

                {/* Progress ring summary */}
                <div className="flex items-center gap-5 bg-white/10 backdrop-blur-sm rounded-2xl px-6 py-4 border border-white/20">
                  <div className="relative w-14 h-14 flex-shrink-0">
                    <svg className="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
                      <circle cx="28" cy="28" r="22" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="5" />
                      <circle
                        cx="28" cy="28" r="22" fill="none"
                        stroke="white" strokeWidth="5"
                        strokeLinecap="round"
                        strokeDasharray={`${2 * Math.PI * 22}`}
                        strokeDashoffset={`${2 * Math.PI * 22 * (1 - completionPercent / 100)}`}
                        style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1)' }}
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-white font-bold text-xs font-display">
                      {completionPercent}%
                    </span>
                  </div>
                  <div>
                    <p className="text-white font-semibold text-lg font-display leading-none">{completedCount}/{tasks.length}</p>
                    <p className="text-white/70 text-xs mt-1 font-body">tasks done</p>
                  </div>
                </div>
              </div>
            </div>

            {/* ── Stat Cards ── */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 stagger-children">

              {/* All */}
              <div className="stat-card card-hover animate-fadeIn group cursor-default">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent-purple)))' }}>
                    <LayoutList className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-3xl font-bold font-display text-gradient">{tasks.length}</span>
                </div>
                <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] font-body">Total Tasks</p>
                <div className="progress-bar mt-3">
                  <div className="progress-bar-fill" style={{ width: '100%' }} />
                </div>
              </div>

              {/* Completed */}
              <div className="stat-card card-hover animate-fadeIn group cursor-default">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
                    <CheckCircle2 className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-3xl font-bold font-display" style={{ color: '#10b981' }}>{completedCount}</span>
                </div>
                <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] font-body">Completed</p>
                <div className="progress-bar mt-3">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${completionPercent}%`,
                      background: 'linear-gradient(90deg, #10b981, #34d399)',
                    }}
                  />
                </div>
              </div>

              {/* Pending */}
              <div className="stat-card card-hover animate-fadeIn group cursor-default">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                    <Clock className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-3xl font-bold font-display" style={{ color: '#f59e0b' }}>{pendingCount}</span>
                </div>
                <p className="text-sm font-medium text-[hsl(var(--muted-foreground))] font-body">Pending</p>
                <div className="progress-bar mt-3">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: tasks.length > 0 ? `${Math.round((pendingCount / tasks.length) * 100)}%` : '0%',
                      background: 'linear-gradient(90deg, #f59e0b, #fcd34d)',
                    }}
                  />
                </div>
              </div>
            </div>

            {/* ── Filters & Add Button Row ── */}
            <div className="flex flex-col gap-4 animate-fadeIn overflow-visible">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search tasks by title or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* Filters & Add Button */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative z-40">
                <div className="flex items-center gap-3 relative z-50">
                  <TaskFilters
                    activeFilter={activeFilter}
                    onFilterChange={setActiveFilter}
                    counts={{
                      all: tasks.length,
                      completed: completedCount,
                      pending: pendingCount,
                    }}
                  />
                  <TaskSort activeSort={sortBy} onSortChange={setSortBy} />
                </div>

                <Button
                  onClick={() => setShowCreateModal(true)}
                  size="lg"
                  className="btn btn-gradient-primary px-6 py-3 text-sm font-semibold gap-2 shadow-lg"
                >
                  <Plus className="w-5 h-5" />
                  Add Task
                </Button>
              </div>
            </div>

            {/* ── Error Message ── */}
            {error && (
              <div className="flex items-start gap-3 p-4 rounded-xl border animate-slideIn"
                style={{
                  background: 'linear-gradient(135deg, rgba(239,68,68,0.08), rgba(220,38,38,0.05))',
                  borderColor: 'rgba(239,68,68,0.25)',
                }}>
                <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: '#ef4444' }} />
                <p className="text-sm font-medium font-body" style={{ color: '#ef4444' }}>{error}</p>
              </div>
            )}

            {/* ── Task List / Loading ── */}
            {loading && tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 animate-fadeIn">
                {/* Spinner with glow */}
                <div className="relative mb-6">
                  <div
                    className="absolute inset-0 rounded-full blur-xl opacity-40"
                    style={{ background: 'hsl(var(--primary))', transform: 'scale(1.5)' }}
                  />
                  <div className="relative w-16 h-16 rounded-full flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent-purple)))' }}>
                    <Loader2 className="w-8 h-8 text-white animate-spin" />
                  </div>
                </div>
                <p className="text-[hsl(var(--muted-foreground))] font-medium font-body text-sm tracking-wide">
                  Loading your tasks...
                </p>
              </div>
            ) : filteredTasks.length === 0 && tasks.length === 0 ? (
              <EmptyState onCreateTask={() => setShowCreateModal(true)} />
            ) : sortedTasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 animate-fadeIn">
                <div className="text-gray-400 text-center">
                  <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-xl font-semibold mb-2">No tasks found</h3>
                  <p className="text-sm">Try adjusting your search or filters</p>
                </div>
              </div>
            ) : (
              <div className="animate-fadeIn">
                <TaskList
                  tasks={sortedTasks}
                  onToggleComplete={handleToggleComplete}
                  onDelete={deleteTask}
                  onEdit={handleEdit}
                />
              </div>
            )}

          </div>
        </main>
      </div>

      {/* ── Create Modal ── */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Task"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* ── Edit Modal ── */}
      <Modal
        isOpen={!!editingTask}
        onClose={() => setEditingTask(null)}
        title="Edit Task"
      >
        {editingTask && (
          <TaskForm
            onSubmit={handleUpdateTask}
            initialTask={editingTask}
            onCancel={() => setEditingTask(null)}
          />
        )}
      </Modal>

      {/* ── Floating Add Button (mobile) ── */}
      <button
        className="fab sm:hidden"
        onClick={() => setShowCreateModal(true)}
        aria-label="Add new task"
      >
        <Plus className="w-6 h-6" />
      </button>

      {/* ── Confetti Animation ── */}
      <Confetti active={showConfetti} onComplete={() => setShowConfetti(false)} />
    </div>
  );
}