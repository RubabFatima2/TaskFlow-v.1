/**
 * MessageList component — displays conversation messages.
 *
 * [Task]: T045
 * [From]: speckit.specify §US6, §US7
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { Bot, User } from 'lucide-react';
import type { ChatMessage } from '@/lib/chat-api';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      role="listitem"
      aria-label={`${isUser ? 'You' : 'TaskFlow AI'}: ${message.content}`}
    >
      {/* Avatar */}
      <div
        className={`
          flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
          ${isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gradient-to-br from-purple-500 to-blue-600 text-white'
          }
        `}
        aria-hidden="true"
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message content */}
      <div
        className={`
          max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed
          ${isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
          }
        `}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {message.timestamp && (
          <time
            className={`
              block text-[10px] mt-1
              ${isUser ? 'text-blue-200' : 'text-gray-400 dark:text-gray-500'}
            `}
            dateTime={message.timestamp}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </time>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3" role="status" aria-label="AI is typing">
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-600 text-white">
        <Bot className="w-4 h-4" />
      </div>
      <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

export default function MessageList({ messages, isLoading = false }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center mb-4 shadow-lg">
          <Bot className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          TaskFlow AI Assistant
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
          I can help you manage your tasks. Try saying:
        </p>
        <div className="mt-3 space-y-1.5 text-xs text-gray-400 dark:text-gray-500">
          <p>&quot;Add buy groceries&quot;</p>
          <p>&quot;Show my tasks&quot;</p>
          <p>&quot;Mark buy groceries as done&quot;</p>
          <p>&quot;Delete the groceries task&quot;</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
      role="list"
      aria-label="Chat messages"
    >
      {messages.map((msg, index) => (
        <MessageBubble key={msg.id || index} message={msg} />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
