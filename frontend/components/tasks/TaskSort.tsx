'use client';

import { ArrowUpDown, Calendar, AlertCircle, Type } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';

export type SortOption = 'date' | 'priority' | 'alphabetical';

interface TaskSortProps {
  activeSort: SortOption;
  onSortChange: (sort: SortOption) => void;
}

export default function TaskSort({ activeSort, onSortChange }: TaskSortProps) {
  const [showDropdown, setShowDropdown] = useState(false);
  const [mounted, setMounted] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showDropdown]);

  const handleButtonClick = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY + 4,
        left: rect.left + window.scrollX,
      });
      setShowDropdown(!showDropdown);
    }
  };

  const sortOptions = [
    { value: 'date' as SortOption, label: 'Due Date', icon: Calendar },
    { value: 'priority' as SortOption, label: 'Priority', icon: AlertCircle },
    { value: 'alphabetical' as SortOption, label: 'Alphabetical', icon: Type },
  ];

  const activeOption = sortOptions.find(opt => opt.value === activeSort);

  const dropdownContent = showDropdown && mounted ? (
    <div
      ref={dropdownRef}
      style={{
        position: 'absolute',
        top: `${dropdownPosition.top}px`,
        left: `${dropdownPosition.left}px`,
        zIndex: 99999,
      }}
      className="w-48 bg-white dark:bg-gray-900 border border-blue-200 dark:border-blue-800/30 rounded-lg shadow-2xl py-2 animate-fadeInFast"
    >
      {sortOptions.map((option) => {
        const Icon = option.icon;
        const isActive = activeSort === option.value;

        return (
          <button
            key={option.value}
            type="button"
            onClick={() => {
              onSortChange(option.value);
              setShowDropdown(false);
            }}
            className={`w-full px-4 py-2 text-left text-sm flex items-center gap-3 transition-colors ${
              isActive
                ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-600 dark:hover:text-blue-400'
            }`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{option.label}</span>
          </button>
        );
      })}
    </div>
  ) : null;

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        onClick={handleButtonClick}
        className="flex items-center gap-2 px-4 py-2 rounded-lg border border-blue-200 dark:border-blue-800/30 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-sm font-medium shadow-sm"
      >
        <ArrowUpDown className="w-4 h-4" />
        <span>Sort: {activeOption?.label}</span>
      </button>

      {mounted && typeof document !== 'undefined' && createPortal(dropdownContent, document.body)}
    </>
  );
}
