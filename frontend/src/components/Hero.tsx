'use client';

import React from 'react';
import { Activity, Cpu, Sparkles, FileText } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-sky-950 via-slate-900 to-slate-900 text-white py-12 px-4 sm:px-6 lg:px-8 shadow-xl">
      {/* Background ECG SVG Grid Pattern */}
      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#0284c7_1px,transparent_1px)] [background-size:16px_16px]"></div>
      
      <div className="relative max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          <div className="lg:col-span-8 space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI-Powered Electrocardiogram Analytics</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Clinical Decision Support for <br className="hidden sm:inline" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-blue-300 to-indigo-200">
                12-Lead ECG Records
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg max-w-3xl leading-relaxed">
              Upload raw WFDB format electrocardiogram headers (<code className="text-sky-300 font-mono text-sm bg-slate-800 px-1.5 py-0.5 rounded">.hea</code>) 
              and signal data (<code className="text-sky-300 font-mono text-sm bg-slate-800 px-1.5 py-0.5 rounded">.dat</code>) 
              for automated feature extraction, multi-output XGBoost classification, and SHAP explainability.
            </p>

            <div className="flex flex-wrap gap-4 pt-2 text-xs sm:text-sm text-slate-300">
              <div className="flex items-center gap-2 bg-slate-800/80 backdrop-blur px-3 py-2 rounded-lg border border-slate-700">
                <Activity className="w-4 h-4 text-sky-400" />
                <span>213 Extracted ECG Features</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-800/80 backdrop-blur px-3 py-2 rounded-lg border border-slate-700">
                <Cpu className="w-4 h-4 text-emerald-400" />
                <span>XGBoost Multi-Output Model</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-800/80 backdrop-blur px-3 py-2 rounded-lg border border-slate-700">
                <FileText className="w-4 h-4 text-purple-400" />
                <span>SHAP Explainability Vectors</span>
              </div>
            </div>
          </div>

          {/* Diagnostic Categories Quick Legend */}
          <div className="lg:col-span-4 bg-slate-800/60 backdrop-blur-md rounded-2xl p-5 border border-slate-700/80 shadow-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Supported Diagnostics</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-700/50">
                <span className="text-xs font-semibold text-emerald-400">NORM</span>
                <span className="text-xs text-slate-300">Normal Sinus Rhythm</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-700/50">
                <span className="text-xs font-semibold text-red-400">MI</span>
                <span className="text-xs text-slate-300">Myocardial Infarction</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-700/50">
                <span className="text-xs font-semibold text-amber-400">CD</span>
                <span className="text-xs text-slate-300">Conduction Disturbance</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-700/50">
                <span className="text-xs font-semibold text-purple-400">HYP</span>
                <span className="text-xs text-slate-300">Ventricular Hypertrophy</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-700/50">
                <span className="text-xs font-semibold text-blue-400">STTC</span>
                <span className="text-xs text-slate-300">ST/T Abnormalities</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
