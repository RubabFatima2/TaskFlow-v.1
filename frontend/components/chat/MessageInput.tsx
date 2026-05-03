/**
 * MessageInput component — text input with send button.
 *
 * [Task]: T046
 * [From]: speckit.specify §US1-US7
 */

'use client';

import React, { useState, useRef } from 'react';
import { Send } from 'lucide-react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message... (e.g. "add buy groceries")',
}: MessageInputProps) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    // Re-focus input after sending
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-3">
      <div className="flex items-end gap-2 max-w-3xl mx-auto">
        <textarea
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          maxLength={5000}
          aria-label="Chat message input"
          className="
            flex-1 resize-none rounded-xl border border-gray-300 dark:border-gray-600
            bg-gray-50 dark:bg-gray-800 px-4 py-2.5
            text-sm text-gray-900 dark:text-gray-100
            placeholder-gray-500 dark:placeholder-gray-400
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors duration-200
            max-h-32 overflow-y-auto
          "
          style={{
            minHeight: '42px',
            height: 'auto',
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = Math.min(target.scrollHeight, 128) + 'px';
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          aria-label="Send message"
          className="
            flex-shrink-0 w-10 h-10 rounded-xl
            bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600
            text-white disabled:text-gray-500
            flex items-center justify-center
            transition-all duration-200
            disabled:cursor-not-allowed
            shadow-sm hover:shadow-md
          "
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
