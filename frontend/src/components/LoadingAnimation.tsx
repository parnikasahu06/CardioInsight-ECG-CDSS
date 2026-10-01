'use client';

import React, { useEffect, useState } from 'react';
import { Activity, Cpu, Sparkles, CheckCircle2 } from 'lucide-react';

const ANALYSIS_STAGES = [
  { id: 1, text: '1. Validating ECG record (.hea + .dat)' },
  { id: 2, text: '2. Reading 12-lead signal waveforms' },
  { id: 3, text: '3. Extracting 322 ECG features' },
  { id: 4, text: '4. Running XGBoost inference' },
  { id: 5, text: '5. Computing SHAP explanations' },
  { id: 6, text: '6. Preparing clinical decision support' },
];

export const LoadingAnimation: React.FC = () => {
  const [activeStage, setActiveStage] = useState<number>(1);

  useEffect(() => {
    const timer1 = setTimeout(() => setActiveStage(2), 600);
    const timer2 = setTimeout(() => setActiveStage(3), 1400);
    const timer3 = setTimeout(() => setActiveStage(4), 2500);
    const timer4 = setTimeout(() => setActiveStage(5), 3800);
    const timer5 = setTimeout(() => setActiveStage(6), 5000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  }, []);

  return (
    <div className="bg-white rounded-2xl p-8 border border-sky-100 shadow-xl text-center space-y-6 max-w-2xl mx-auto">
      {/* Animated ECG Waveform Container */}
      <div className="relative w-full h-32 bg-slate-900 rounded-2xl overflow-hidden flex items-center justify-center border border-slate-800 shadow-inner">
        {/* ECG Grid lines */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:12px_12px] opacity-40"></div>

        {/* Dynamic SVG ECG Wave */}
        <svg className="w-full h-24 stroke-sky-400 fill-none" viewBox="0 0 500 100" preserveAspectRatio="none">
          <path
            d="M 0 50 L 80 50 L 90 40 L 100 60 L 110 50 L 140 50 L 150 15 L 165 90 L 180 35 L 195 50 L 230 50 L 245 42 L 260 55 L 270 50 L 330 50 L 340 10 L 355 95 L 370 30 L 385 50 L 500 50"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="animate-ecg-beat"
            style={{
              strokeDasharray: '1000',
              strokeDashoffset: '1000',
              animation: 'ecgBeat 2.5s ease-in-out infinite',
              filter: 'drop-shadow(0px 0px 6px #0284c7)'
            }}
          />
        </svg>

        {/* Pulse Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-sky-500/10 to-transparent animate-pulse"></div>

        <div className="absolute bottom-3 left-4 flex items-center gap-2 text-xs text-sky-400 font-mono">
          <Activity className="w-4 h-4 animate-spin text-sky-400" />
          <span>SAMPLING RATE: 500 Hz | LEAD II ANALYZER</span>
        </div>
      </div>

      {/* Text status */}
      <div className="space-y-2">
        <h3 className="text-xl font-bold text-slate-800 tracking-tight flex items-center justify-center gap-2">
          <Cpu className="w-5 h-5 text-sky-600 animate-pulse" />
          <span>Analyzing Electrocardiogram Signal</span>
        </h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Our machine learning pipeline is processing 12-lead signal waveforms to detect cardiac abnormalities.
        </p>
      </div>

      {/* Multi-step Progress List */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-left space-y-2.5 max-w-lg mx-auto">
        {ANALYSIS_STAGES.map(stage => {
          const isDone = stage.id < activeStage;
          const isCurrent = stage.id === activeStage;

          return (
            <div key={stage.id} className="flex items-center gap-3 text-xs">
              <div className="flex-shrink-0">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : isCurrent ? (
                  <div className="w-4 h-4 rounded-full border-2 border-sky-600 border-t-transparent animate-spin"></div>
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300"></div>
                )}
              </div>
              <span className={`font-medium ${
                isDone
                  ? 'text-slate-500 line-through decoration-slate-300'
                  : isCurrent
                  ? 'text-sky-800 font-semibold'
                  : 'text-slate-400'
              }`}>
                {stage.text}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
