'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';
import { AuthGuard } from '@/components/AuthGuard';
import { Key, Shield, User as UserIcon, Save, Check } from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { useAnalysisStore } from '@/store/useAnalysisStore';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { apiKey, setApiKey } = useAnalysisStore();
  const [localKey, setLocalKey] = useState(apiKey);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setApiKey(localKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-slate-950">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />
          <main className="p-8 space-y-8 max-w-4xl mx-auto w-full">
            <div>
              <h1 className="text-2xl font-heading font-extrabold text-white">Platform Settings</h1>
              <p className="text-sm text-slate-400 mt-1">Configure AI API keys, preferences, and security options.</p>
            </div>

            {/* Profile Info */}
            <div className="dark-glass-card rounded-3xl p-8 shadow-2xl space-y-6">
              <h3 className="text-lg font-heading font-bold text-white border-b border-slate-900 pb-4 flex items-center gap-2">
                <UserIcon className="w-4 h-4 text-indigo-400" />
                User Profile Information
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Full Name</label>
                  <p className="font-semibold text-slate-200 mt-0.5">{user?.name}</p>
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Email Address</label>
                  <p className="font-semibold text-slate-200 mt-0.5">{user?.email}</p>
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Account Role</label>
                  <span className="inline-block mt-0.5 px-2.5 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-300 rounded-full border border-indigo-500/20">
                    {user?.role?.toUpperCase()}
                  </span>
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Subscription Plan</label>
                  <p className="font-semibold text-slate-200 mt-0.5 uppercase">{user?.subscription}</p>
                </div>
              </div>
            </div>

            {/* API Credentials */}
            <form onSubmit={handleSave} className="dark-glass-card rounded-3xl p-8 shadow-2xl space-y-6">
              <h3 className="text-lg font-heading font-bold text-white border-b border-slate-900 pb-4 flex items-center gap-2">
                <Key className="w-4 h-4 text-purple-400" />
                Custom AI Model Key Overrides
              </h3>
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Groq / OpenAI API Key (Optional Override)
                </label>
                <input
                  type="password"
                  value={localKey}
                  onChange={(e) => setLocalKey(e.target.value)}
                  placeholder="gsk_... or sk-..."
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-900 focus:border-indigo-500/40 text-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500/40 transition-all duration-300"
                />
                <p className="text-[11px] text-slate-500 mt-1.5">
                  If left blank, backend will default to production Groq Llama-3.1 API key.
                </p>
              </div>

              <button
                type="submit"
                className="px-6 py-3 bg-indigo-500 hover:bg-indigo-400 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-500/20 flex items-center gap-2 transition-all duration-200"
              >
                {saved ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Save className="w-3.5 h-3.5" />}
                {saved ? 'Key Saved Successfully' : 'Save Settings'}
              </button>
            </form>
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
