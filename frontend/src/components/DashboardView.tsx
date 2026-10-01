'use client';

import React from 'react';
import { Activity, Upload, Server, ShieldCheck, FileCode, CheckCircle2, ArrowRight, Layers, Cpu } from 'lucide-react';
import { ECGPredictionResponse } from '@/types/ecg';

interface DashboardViewProps {
  onNavigateToUpload: () => void;
  onNavigateToAnalysis: () => void;
  hasAnalysis: boolean;
  result: ECGPredictionResponse | null;
  isHealthy: boolean | null;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onNavigateToUpload,
  onNavigateToAnalysis,
  hasAnalysis,
  result,
  isHealthy,
}) => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Hero Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-blue-950 text-white rounded-3xl p-8 sm:p-10 shadow-xl border border-slate-800 relative overflow-hidden">
        {/* Background ECG watermark */}
        <div className="absolute right-[-30px] bottom-[-30px] opacity-10 pointer-events-none">
          <Activity className="w-80 h-80 text-sky-400" />
        </div>

        <div className="relative z-10 space-y-4 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/20 text-sky-300 border border-sky-400/30 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Explainable AI-Based ECG Clinical Decision Support System</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            CardioInsight
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
            AI-assisted ECG analysis and explainable clinical decision support for 12-lead PTB-XL ECG records.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <button
              onClick={onNavigateToUpload}
              className="inline-flex items-center gap-2 bg-sky-500 hover:bg-sky-400 text-white text-xs font-bold px-5 py-3 rounded-xl transition-all shadow-lg shadow-sky-500/25"
            >
              <Upload className="w-4 h-4" />
              <span>Upload ECG Record</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            {hasAnalysis && (
              <button
                onClick={onNavigateToAnalysis}
                className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white text-xs font-bold px-5 py-3 rounded-xl border border-white/20 transition-all"
              >
                <Activity className="w-4 h-4 text-sky-300" />
                <span>View Current Analysis</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Active Analysis Summary Card (If an analysis exists) */}
      {hasAnalysis && result && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border-2 border-sky-500/40 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center font-bold">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">Active Analysis Result</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Record: <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{result.record_info?.record_id || 'WFDB Upload'}</span>
                </p>
              </div>
            </div>

            <button
              onClick={onNavigateToAnalysis}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/80 border border-sky-200 dark:border-sky-800 px-4 py-2 rounded-xl hover:bg-sky-100 transition-colors"
            >
              <span>Open Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs">
            <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Primary AI Finding</span>
              <span className="text-base font-extrabold text-slate-900 dark:text-white">{result.diagnosis}</span>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Model Confidence</span>
              <span className="text-base font-extrabold text-emerald-600 dark:text-emerald-400">{result.confidence.toFixed(2)}%</span>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Review Priority</span>
              <span className="text-base font-extrabold text-slate-900 dark:text-white">{result.risk_level} Priority</span>
            </div>
          </div>
        </div>
      )}

      {/* 3 Clinician Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: System Status */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 flex items-center justify-center">
            <Server className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900 dark:text-white">System Status</h3>
          <div className="text-xs text-slate-600 dark:text-slate-300 space-y-2 pt-1">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-1.5">
              <span>Backend API</span>
              <span className={`font-bold ${isHealthy ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'}`}>
                {isHealthy === null ? 'Checking...' : isHealthy ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-1.5">
              <span>AI Model Engine</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">Ready</span>
            </div>
            <div className="flex items-center justify-between">
              <span>ECG Processing</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">Ready</span>
            </div>
          </div>
        </div>

        {/* Card 2: AI Analysis Engine */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-3">
          <div className="w-10 h-10 rounded-xl bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900 dark:text-white">AI Analysis Engine</h3>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
            322 extracted (274 preprocessed) ECG features analyzed using a multi-output XGBoost classifier with SHAP-based explainability.
          </p>
        </div>

        {/* Card 3: Supported ECG Format */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 flex items-center justify-center">
            <FileCode className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900 dark:text-white">Supported ECG Format</h3>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
            PTB-XL 12-lead WFDB paired header (<span className="font-mono font-bold text-sky-700 dark:text-sky-400">.hea</span>) and binary signal (<span className="font-mono font-bold text-sky-700 dark:text-sky-400">.dat</span>) files.
          </p>
        </div>
      </div>
    </div>
  );
};
