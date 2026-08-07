'use client';

import React from 'react';
import {
  LayoutDashboard,
  Upload,
  Activity,
  LineChart,
  Layers,
  UserCheck,
  FileText,
  PlusCircle,
  Server,
  AlertCircle,
  X
} from 'lucide-react';

export type SectionId =
  | 'dashboard'
  | 'upload'
  | 'analysis'
  | 'waveform'
  | 'explanation'
  | 'review'
  | 'report';

interface SidebarProps {
  activeSection: SectionId;
  onSelectSection: (section: SectionId) => void;
  onNewAnalysis: () => void;
  hasAnalysis: boolean;
  isHealthy: boolean | null;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSelectSection,
  onNewAnalysis,
  hasAnalysis,
  isHealthy,
  isOpenMobile,
  onCloseMobile,
}) => {
  const navItems: { id: SectionId; label: string; icon: React.FC<{ className?: string }>; disabled?: boolean }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload ECG', icon: Upload },
    { id: 'analysis', label: 'Analysis', icon: Activity, disabled: !hasAnalysis },
    { id: 'waveform', label: 'ECG Waveform', icon: LineChart, disabled: !hasAnalysis },
    { id: 'explanation', label: 'AI Explanation', icon: Layers, disabled: !hasAnalysis },
    { id: 'review', label: 'Clinical Review', icon: UserCheck, disabled: !hasAnalysis },
    { id: 'report', label: 'Report', icon: FileText, disabled: !hasAnalysis },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 transition-colors">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-blue-700 flex items-center justify-center shadow-md shadow-sky-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">CardioInsight</span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Explainable AI CDSS</p>
          </div>
        </div>

        {/* Mobile close button */}
        <button
          onClick={onCloseMobile}
          className="md:hidden p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          Clinical Workflow
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          const isDisabled = item.disabled;

          return (
            <button
              key={item.id}
              onClick={() => {
                if (!isDisabled) {
                  onSelectSection(item.id);
                  onCloseMobile();
                }
              }}
              disabled={isDisabled}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-sky-600 text-white shadow-md shadow-sky-500/20'
                  : isDisabled
                  ? 'text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/30 cursor-not-allowed border border-slate-100 dark:border-slate-800/50'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : isDisabled ? 'text-slate-400 dark:text-slate-500' : 'text-slate-500 dark:text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {isDisabled && (
                <span className="text-[10px] text-slate-400 dark:text-slate-500 font-bold bg-slate-200/60 dark:bg-slate-700/60 px-1.5 py-0.5 rounded">
                  Pending
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Section: New Analysis & Backend Status */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
        {/* + New Analysis button */}
        <button
          onClick={() => {
            onNewAnalysis();
            onCloseMobile();
          }}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 transition-all shadow-md"
        >
          <PlusCircle className="w-4 h-4 text-sky-400 dark:text-white" />
          <span>+ New Analysis</span>
        </button>

        {/* Backend Status Indicator */}
        <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs">
          <div className="flex items-center gap-2">
            <Server className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            <span className="text-[11px] font-medium text-slate-600 dark:text-slate-300">Backend</span>
          </div>

          {isHealthy === null ? (
            <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-ping"></span>
              Checking...
            </span>
          ) : isHealthy ? (
            <span className="text-[11px] text-emerald-700 dark:text-emerald-400 font-bold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Backend Online
            </span>
          ) : (
            <span className="text-[11px] text-red-700 dark:text-red-400 font-bold flex items-center gap-1.5">
              <AlertCircle className="w-3 h-3 text-red-500" />
              Backend Offline
            </span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside className="hidden md:block w-64 fixed top-0 bottom-0 left-0 z-40">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm md:hidden"
        />
      )}

      {/* Mobile Drawer Sidebar */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out md:hidden ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
};
