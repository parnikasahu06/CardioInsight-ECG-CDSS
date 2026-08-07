'use client';

import React from 'react';
import { Menu, Sun, Moon, ShieldCheck, Activity, FileCheck } from 'lucide-react';
import { useTheme } from './ThemeContext';
import { RecordInfo } from '@/types/ecg';

interface HeaderProps {
  onOpenMobileMenu: () => void;
  recordInfo?: RecordInfo;
  diagnosis?: string;
  hasAnalysis: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenMobileMenu,
  recordInfo,
  diagnosis,
  hasAnalysis,
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-white/90 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30 backdrop-blur-md transition-colors">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left Section: Mobile Menu Trigger + Brand context */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileMenu}
            className="md:hidden p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Open Navigation Menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Sticky Active Analysis Context Bar */}
          {hasAnalysis ? (
            <div className="flex items-center gap-2 bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 px-3 py-1.5 rounded-xl text-xs">
              <Activity className="w-4 h-4 text-sky-600 dark:text-sky-400" />
              <div className="flex items-center gap-2">
                <span className="font-bold text-sky-900 dark:text-sky-200 font-mono">
                  Record: {recordInfo?.record_id || 'WFDB ECG'}
                </span>
                <span className="hidden sm:inline text-sky-400 dark:text-sky-600">•</span>
                <span className="hidden sm:inline text-sky-800 dark:text-sky-300 font-medium">
                  {recordInfo?.n_leads || 12}-Lead ECG
                </span>
                <span className="text-sky-400 dark:text-sky-600">•</span>
                <span className="font-extrabold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                  <FileCheck className="w-3.5 h-3.5" />
                  Analysis Complete ({diagnosis})
                </span>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-800 dark:text-white tracking-tight">CardioInsight</span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium hidden sm:inline">
                • Explainable AI ECG CDSS
              </span>
            </div>
          )}
        </div>

        {/* Right Section: System badges & Theme Switcher */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 text-xs font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>XGBoost Multi-Output Pipeline</span>
          </div>

          {/* Theme Switcher Button — ONLY ONE ICON */}
          <button
            onClick={toggleTheme}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 text-xs font-bold transition-all shadow-sm"
            aria-label="Toggle Theme"
          >
            {theme === 'light' ? (
              <>
                <Moon className="w-4 h-4 text-indigo-600" />
                <span>Dark</span>
              </>
            ) : (
              <>
                <Sun className="w-4 h-4 text-amber-400" />
                <span>Light</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
