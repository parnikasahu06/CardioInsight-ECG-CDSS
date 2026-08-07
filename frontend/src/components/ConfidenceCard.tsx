'use client';

import React from 'react';
import { Target, TrendingUp, HelpCircle } from 'lucide-react';

interface ConfidenceCardProps {
  confidence: number;
}

export const ConfidenceCard: React.FC<ConfidenceCardProps> = ({ confidence }) => {
  const normalizedConfidence = Math.min(Math.max(confidence, 0), 100);

  const getConfidenceLevel = (val: number) => {
    if (val >= 85) return { label: 'High Certainty', color: 'text-emerald-700', barBg: 'bg-emerald-500' };
    if (val >= 60) return { label: 'Moderate Certainty', color: 'text-amber-700', barBg: 'bg-amber-500' };
    return { label: 'Low Certainty', color: 'text-red-700', barBg: 'bg-red-500' };
  };

  const levelInfo = getConfidenceLevel(normalizedConfidence);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg flex flex-col justify-between h-full transition-colors">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Prediction Confidence</span>
          <div className="flex items-center gap-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors cursor-help">
            <Target className="w-4 h-4" />
          </div>
        </div>

        <div className="flex items-baseline justify-between mb-2">
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {normalizedConfidence.toFixed(1)}
            </span>
            <span className="text-xl font-bold text-slate-500 dark:text-slate-400">%</span>
          </div>

          <span className={`text-xs font-bold px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 ${levelInfo.color}`}>
            {levelInfo.label}
          </span>
        </div>

        {/* Progress gauge bar */}
        <div className="w-full bg-slate-100 dark:bg-slate-800 h-3.5 rounded-full overflow-hidden p-0.5 border border-slate-200/60 dark:border-slate-700 mb-4">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${levelInfo.barBg}`}
            style={{ width: `${normalizedConfidence}%` }}
          ></div>
        </div>

        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Confidence reflects the calibrated model probability score assigned by the ensemble classifier to the top predicted diagnostic class.
        </p>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span className="flex items-center gap-1">
          <TrendingUp className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
          Model Metric
        </span>
        <span className="font-bold text-slate-900 dark:text-white">XGBoost Softmax</span>
      </div>
    </div>
  );
};
