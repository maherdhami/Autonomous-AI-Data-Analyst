'use client';

import React from 'react';
import { Search, Bell, Sparkles, ShieldCheck } from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';

export function Navbar() {
  const { user } = useAuthStore();

  return (
    <header className="h-16 bg-slate-950/70 border-b border-slate-900/80 px-8 flex items-center justify-between sticky top-0 z-20 backdrop-blur-md">
      {/* Search Bar */}
      <div className="flex items-center gap-3 w-96 bg-slate-900/40 px-3.5 py-2 rounded-xl border border-slate-900 focus-within:border-indigo-500/40 focus-within:bg-slate-900/60 focus-within:ring-1 focus-within:ring-indigo-500/40 transition-all duration-300">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search analyses, datasets, insights..."
          className="bg-transparent border-none text-xs text-slate-200 placeholder-slate-500 focus:outline-none w-full"
        />
      </div>

      {/* Action Badges & Profile */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold rounded-full">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>FastAPI + Firebase Connected</span>
        </div>

        <button className="p-2 text-slate-400 hover:text-indigo-400 hover:bg-slate-900/50 rounded-xl transition-all duration-200 relative border border-transparent hover:border-slate-800">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
        </button>

        <div className="flex items-center gap-3 pl-3 border-l border-slate-900">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-indigo-500/10">
            {user?.name?.[0] || 'A'}
          </div>
        </div>
      </div>
    </header>
  );
}
