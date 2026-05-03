/**
 * Chat page — AI-powered task management via conversation.
 *
 * [Task]: T047
 * [From]: speckit.specify §US1-US7
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import ChatInterface from '@/components/chat/ChatInterface';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ChatPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-gray-500 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
      {/* Top bar */}
      <header className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <Link
          href="/tasks"
          className="
            flex items-center gap-1.5 px-3 py-1.5 rounded-lg
            text-sm text-gray-600 dark:text-gray-400
            hover:bg-gray-100 dark:hover:bg-gray-800
            transition-colors duration-200
          "
          aria-label="Back to tasks"
        >
          <ArrowLeft className="w-4 h-4" />
          Tasks
        </Link>
        <div className="h-5 w-px bg-gray-200 dark:bg-gray-700" />
        <h1 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          AI Chat Assistant
        </h1>
      </header>

      {/* Chat area */}
      <main className="flex-1 flex p-4 max-w-3xl mx-auto w-full">
        <ChatInterface />
      </main>
    </div>
  );
}
