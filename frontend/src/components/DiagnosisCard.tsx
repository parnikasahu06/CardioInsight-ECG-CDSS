'use client';

import React from 'react';
import { Activity, AlertTriangle, HeartPulse, CheckCircle, ShieldAlert } from 'lucide-react';
import { DIAGNOSIS_DETAILS, DiagnosticClass } from '@/types/ecg';

interface DiagnosisCardProps {
  diagnosis: DiagnosticClass;
  decisionStatus?: string;
  confidence?: number;
  thresholds?: Record<string, number>;
  positiveClasses?: string[];
}

export const DiagnosisCard: React.FC<DiagnosisCardProps> = ({
  diagnosis,
  decisionStatus,
  confidence,
  thresholds,
  positiveClasses = [],
}) => {
  const isNoClassAbove = decisionStatus === 'no_class_above_threshold';
  const threshVal = thresholds?.[diagnosis] !== undefined ? Math.round(thresholds[diagnosis] * 100) : null;

  const details = DIAGNOSIS_DETAILS[diagnosis] || {
    title: `ECG Pattern: ${diagnosis}`,
    category: "Diagnostic Classification",
    description: "Classification returned by XGBoost model.",
    badgeColor: "bg-slate-100 text-slate-800 border-slate-300"
  };

  const otherPositive = positiveClasses.filter((c) => c !== diagnosis);

  const getIcon = () => {
    if (isNoClassAbove) {
      return <AlertTriangle className="w-8 h-8 text-amber-600" />;
    }
    switch (diagnosis) {
      case 'NORM':
        return <CheckCircle className="w-8 h-8 text-emerald-600" />;
      case 'MI':
        return <AlertTriangle className="w-8 h-8 text-red-600" />;
      case 'CD':
        return <Activity className="w-8 h-8 text-amber-600" />;
      case 'HYP':
        return <HeartPulse className="w-8 h-8 text-purple-600" />;
      case 'STTC':
        return <ShieldAlert className="w-8 h-8 text-blue-600" />;
      default:
        return <Activity className="w-8 h-8 text-sky-600" />;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg relative overflow-hidden flex flex-col justify-between h-full transition-colors">
      {/* Decorative accent top stripe */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 ${
        isNoClassAbove ? 'bg-amber-500' :
        diagnosis === 'NORM' ? 'bg-emerald-500' :
        diagnosis === 'MI' ? 'bg-red-500' :
        diagnosis === 'CD' ? 'bg-amber-500' :
        diagnosis === 'HYP' ? 'bg-purple-500' : 'bg-blue-500'
      }`}></div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">AI Model Finding</span>
          <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
            isNoClassAbove ? 'bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-800' : details.badgeColor
          }`}>
            {isNoClassAbove ? 'Below Threshold' : details.category}
          </span>
        </div>

        <div className="flex items-start gap-4 mb-4">
          <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm flex-shrink-0">
            {getIcon()}
          </div>
          <div>
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {isNoClassAbove ? 'No class above decision threshold' : details.title}
            </h3>
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-0.5">
              {isNoClassAbove
                ? `Highest score: ${diagnosis} ${confidence ? confidence.toFixed(1) : ''}%${threshVal ? ` (threshold ${threshVal}%)` : ''}`
                : otherPositive.length > 0
                ? `Primary Finding (Additional positive classes: ${otherPositive.join(', ')})`
                : 'XGBoost Primary Diagnostic Class'}
            </p>
          </div>
        </div>

        <div className="bg-slate-50 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700 space-y-2">
          <p className="text-slate-700 dark:text-slate-300 text-xs leading-relaxed font-medium">
            {isNoClassAbove
              ? 'No diagnostic class reached its decision threshold. The highest-scoring class is shown for reference only. Clinician review advised.'
              : details.description}
          </p>
          <p className="text-[11px] text-sky-800 dark:text-sky-300 font-semibold bg-sky-50 dark:bg-sky-950/80 p-2 rounded-lg border border-sky-100 dark:border-sky-800">
            This is an AI-generated classification based on the uploaded ECG and should be reviewed by a qualified clinician.
          </p>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{isNoClassAbove ? 'Highest Scoring Class' : 'Standard Diagnostic Code'}</span>
        <span className="font-mono font-bold text-slate-900 dark:text-white">
          {diagnosis}{isNoClassAbove && confidence ? ` (${confidence.toFixed(1)}%)` : ''}
        </span>
      </div>
    </div>
  );
};

