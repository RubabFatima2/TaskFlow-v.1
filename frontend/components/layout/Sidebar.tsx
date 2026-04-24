// 'use client';

// import Link from 'next/link';
// import { usePathname } from 'next/navigation';
// import { LayoutDashboard, CheckSquare, Settings, LogOut, CheckCircle2 } from 'lucide-react';

// interface SidebarProps {
//   onLogout: () => void;
// }

// export default function Sidebar({ onLogout }: SidebarProps) {
//   const pathname = usePathname();

//   const navItems = [
//     {
//       name: 'Dashboard',
//       href: '/tasks',
//       icon: LayoutDashboard,
//     },
//     {
//       name: 'Tasks',
//       href: '/tasks',
//       icon: CheckSquare,
//     },
//     {
//       name: 'Settings',
//       href: '/settings',
//       icon: Settings,
//     },
//   ];

//   const isActive = (href: string) => pathname === href;

//   return (
//     <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col h-screen sticky top-0">
//       {/* Logo */}
//       <div className="p-6 border-b border-gray-200 dark:border-gray-800">
//         <Link href="/tasks" className="flex items-center gap-3 group">
//           <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg glow-indigo group-hover:scale-110 transition-transform">
//             <CheckCircle2 className="w-6 h-6 text-white" />
//           </div>
//           <div>
//             <h1 className="text-xl font-bold text-gradient">TaskFlow</h1>
//             <p className="text-xs text-gray-500 dark:text-gray-400">Manage your tasks</p>
//           </div>
//         </Link>
//       </div>

//       {/* Navigation */}
//       <nav className="flex-1 p-4 space-y-2">
//         {navItems.map((item) => {
//           const Icon = item.icon;
//           const active = isActive(item.href);

//           return (
//             <Link
//               key={item.name}
//               href={item.href}
//               className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
//                 active
//                   ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg glow-indigo'
//                   : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
//               }`}
//             >
//               <Icon className={`w-5 h-5 ${active ? 'text-white' : 'text-gray-500 dark:text-gray-400 group-hover:text-indigo-500'}`} />
//               <span className="font-medium">{item.name}</span>
//             </Link>
//           );
//         })}
//       </nav>

//       {/* Logout */}
//       <div className="p-4 border-t border-gray-200 dark:border-gray-800">
//         <button
//           onClick={onLogout}
//           className="flex items-center gap-3 px-4 py-3 rounded-lg w-full text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200 group"
//         >
//           <LogOut className="w-5 h-5" />
//           <span className="font-medium">Logout</span>
//         </button>
//       </div>
//     </aside>
//   );
// }
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import {
  LayoutDashboard, CheckSquare,
  LogOut, CheckCircle2, ChevronLeft,
} from 'lucide-react';

interface SidebarProps {
  onLogout: () => void;
}

export default function Sidebar({ onLogout }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { name: 'Dashboard', href: '/tasks', icon: LayoutDashboard },
    { name: 'Tasks',     href: '/tasks', icon: CheckSquare },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <aside
      className={`
        flex flex-col h-screen sticky top-0
        bg-white dark:bg-gray-950 dark:dark:bg-black
        border-r border-blue-200 dark:border-blue-900/30 dark:dark:border-blue-800/20
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-[68px]' : 'w-64'}
      `}
    >
      {/* ── Logo ── */}
      <div className="p-4 border-b border-blue-200 dark:border-blue-900/30 dark:dark:border-blue-800/20 flex items-center gap-3 overflow-hidden">
        <Link href="/tasks" className="flex items-center gap-3 min-w-0 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center shadow-md flex-shrink-0 transition-transform duration-200 group-hover:scale-110">
            <CheckCircle2 className="w-5 h-5 text-white" />
          </div>
          <div
            className="overflow-hidden transition-all duration-300"
            style={{ width: collapsed ? 0 : 120, opacity: collapsed ? 0 : 1 }}
          >
            <h1 className="text-base font-bold text-gradient whitespace-nowrap">TaskFlow</h1>
            <p className="text-xs text-blue-600 dark:text-blue-400/70 whitespace-nowrap">Manage your tasks</p>
          </div>
        </Link>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(v => !v)}
          className={`
            ml-auto flex-shrink-0 w-6 h-6 rounded-md
            flex items-center justify-center
            text-blue-600 dark:text-blue-400/60 hover:text-blue-700 dark:hover:text-blue-300
            hover:bg-blue-50 dark:hover:bg-blue-900/20
            transition-all duration-300
            ${collapsed ? 'rotate-180' : ''}
          `}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* ── Nav ── */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-hidden">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <div key={item.name} className="relative group/item">
              <Link
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg
                  transition-all duration-200 overflow-hidden
                  ${active
                    ? 'bg-blue-50 dark:bg-blue-600/20 text-blue-600 dark:text-blue-400 shadow-sm dark:shadow-lg dark:shadow-blue-500/10'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-600 dark:hover:text-blue-300'
                  }
                `}
              >
                {/* Active indicator bar */}
                <span
                  className={`
                    absolute left-0 top-1/4 bottom-1/4 w-0.5 rounded-r-full
                    bg-blue-600 dark:bg-blue-500 transition-all duration-200
                    ${active ? 'opacity-100' : 'opacity-0'}
                  `}
                />

                <Icon
                  className={`
                    w-5 h-5 flex-shrink-0 transition-colors duration-200
                    ${active
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-500 group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400'
                    }
                  `}
                />

                <span
                  className="font-medium text-sm whitespace-nowrap transition-all duration-300 overflow-hidden"
                  style={{ width: collapsed ? 0 : 120, opacity: collapsed ? 0 : 1 }}
                >
                  {item.name}
                </span>
              </Link>

              {/* Tooltip when collapsed */}
              {collapsed && (
                <div
                  className="
                    pointer-events-none absolute left-14 top-1/2 -translate-y-1/2 z-50
                    px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap
                    bg-blue-600 text-white
                    opacity-0 group-hover/item:opacity-100
                    translate-x-1 group-hover/item:translate-x-0
                    transition-all duration-150 shadow-lg
                  "
                >
                  {item.name}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* ── Logout ── */}
      <div className="p-2 border-t border-blue-200 dark:border-blue-900/30 dark:dark:border-blue-800/20">
        <div className="relative group/logout">
          <button
            onClick={onLogout}
            className="
              flex items-center gap-3 px-3 py-2.5 rounded-lg w-full
              text-gray-600 dark:text-gray-400
              hover:bg-red-50 dark:hover:bg-red-900/20
              hover:text-red-600 dark:hover:text-red-400
              transition-all duration-200 overflow-hidden
            "
          >
            <LogOut className="w-5 h-5 flex-shrink-0 transition-colors duration-200" />
            <span
              className="font-medium text-sm whitespace-nowrap transition-all duration-300 overflow-hidden"
              style={{ width: collapsed ? 0 : 80, opacity: collapsed ? 0 : 1 }}
            >
              Logout
            </span>
          </button>

          {/* Tooltip when collapsed */}
          {collapsed && (
            <div
              className="
                pointer-events-none absolute left-14 top-1/2 -translate-y-1/2 z-50
                px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap
                bg-blue-600 text-white
                opacity-0 group-hover/logout:opacity-100
                translate-x-1 group-hover/logout:translate-x-0
                transition-all duration-150 shadow-lg
              "
            >
              Logout
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}