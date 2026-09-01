'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  UploadCloud, 
  BarChart3, 
  MessageSquareCode, 
  History, 
  Settings, 
  Zap, 
  LogOut 
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Data Upload', href: '/upload', icon: UploadCloud },
  { name: 'Analysis Results', href: '/analysis', icon: BarChart3 },
  { name: 'AI Chat Analyst', href: '/chat', icon: MessageSquareCode },
  { name: 'Analysis History', href: '/history', icon: History },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-64 bg-slate-950/90 border-r border-slate-900/80 text-slate-300 flex flex-col h-screen sticky top-0 z-30 backdrop-blur-xl">
      {/* Brand Header */}
      <div className="p-6 flex items-center gap-3 border-b border-slate-900/80">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-heading font-bold text-white text-lg leading-tight">AI Analyst</h1>
          <span className="text-[10px] font-bold tracking-wider text-indigo-400 uppercase">Enterprise SaaS</span>
        </div>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 border ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-indigo-500/30 text-white shadow-[0_0_15px_rgba(99,102,241,0.15)] font-semibold'
                  : 'border-transparent hover:bg-slate-900/40 text-slate-400 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-white'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="p-4 border-t border-slate-900/80 bg-slate-950/80">
        <div className="flex items-center justify-between mb-3 px-2">
          <div className="truncate pr-1">
            <p className="text-xs font-semibold text-white truncate">{user?.name || 'Enterprise Analyst'}</p>
            <p className="text-[10px] text-slate-400 truncate mt-0.5">{user?.email || 'analyst@enterprise.com'}</p>
          </div>
          <span className="px-2 py-0.5 text-[9px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded-full shrink-0">
            {user?.role?.toUpperCase() || 'ADMIN'}
          </span>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 rounded-xl transition-all duration-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
