/**
 * ChatInterface — main chat container component.
 *
 * [Task]: T044, T040, T050, T051
 * [From]: speckit.specify §US1-US7
 *
 * Manages message state, conversation_id persistence,
 * API calls, error handling, and loading states.
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { sendChatMessage, getConversationMessages, ChatMessage } from '@/lib/chat-api';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // [Issue 2] Load previous messages on mount
  useEffect(() => {
    const storedConversationId = localStorage.getItem('conversationId');
    if (storedConversationId) {
      setConversationId(storedConversationId);
      setIsLoading(true);
      getConversationMessages(storedConversationId)
        .then((response) => {
          const loadedMessages: ChatMessage[] = response.messages.map((m) => ({
            id: m.id,
            role: m.role as 'user' | 'assistant',
            content: m.content,
            timestamp: m.created_at,
          }));
          setMessages(loadedMessages);
        })
        .catch(() => {
          // Failed to load messages, start fresh
          localStorage.removeItem('conversationId');
          setConversationId(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, []);

  // Persist conversationId to localStorage
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('conversationId', conversationId);
    } else {
      localStorage.removeItem('conversationId');
    }
  }, [conversationId]);

  const handleSend = useCallback(async (message: string) => {
    // Clear any previous error
    setError(null);

    // Add user message to UI immediately
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(message, conversationId);

      // [Task]: T040 — Persist conversation_id
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMsg: ChatMessage = {
        id: response.message_id || `resp-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMsg]);

    } catch (err: unknown) {
      // [Task]: T050 — Error handling
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';

      if (errorMessage.includes('401') || errorMessage.toLowerCase().includes('not authenticated')) {
        setError('Your session has expired. Please log in again.');
      } else if (errorMessage.includes('403')) {
        setError('You do not have access to this conversation.');
      } else if (errorMessage.includes('503')) {
        setError('AI service is temporarily unavailable. Please try again shortly.');
      } else if (errorMessage.includes('429')) {
        setError('Too many requests. Please wait a moment before trying again.');
      } else {
        setError('Failed to send message. Please try again.');
      }

      // Remove the optimistic user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            TaskFlow AI
          </h2>
        </div>
        <button
          onClick={handleNewConversation}
          className="
            flex items-center gap-1.5 px-3 py-1.5 rounded-lg
            text-xs font-medium text-gray-600 dark:text-gray-400
            hover:bg-gray-100 dark:hover:bg-gray-700
            transition-colors duration-200
          "
          aria-label="Start new conversation"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          New Chat
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div
          className="mx-4 mt-3 px-4 py-2.5 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-2"
          role="alert"
        >
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-600 text-xs"
            aria-label="Dismiss error"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <MessageInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
