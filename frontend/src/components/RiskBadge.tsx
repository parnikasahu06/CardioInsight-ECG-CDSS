'use client';

import React from 'react';
import { ShieldCheck, AlertCircle, AlertTriangle } from 'lucide-react';
import { RiskLevel } from '@/types/ecg';

interface RiskBadgeProps {
  riskLevel: RiskLevel;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ riskLevel }) => {
  const getRiskConfig = (level: RiskLevel) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return {
          title: 'Low Review Priority',
          color: 'bg-emerald-50 text-emerald-800 border-emerald-200',
          badgeBg: 'bg-emerald-600 text-white',
          icon: <ShieldCheck className="w-6 h-6 text-emerald-600" />,
          description: 'High model certainty or normal baseline pattern. Standard routine clinician review recommended.'
        };
      case 'medium':
        return {
          title: 'Medium Review Priority',
          color: 'bg-amber-50 text-amber-800 border-amber-200',
          badgeBg: 'bg-amber-500 text-white',
          icon: <AlertCircle className="w-6 h-6 text-amber-600" />,
          description: 'Moderate model uncertainty or secondary class outputs detected. Detailed clinician review advised.'
        };
      case 'high':
        return {
          title: 'High Review Priority',
          color: 'bg-red-50 text-red-800 border-red-200',
          badgeBg: 'bg-red-600 text-white',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          description: 'Ischemic or critical conduction pattern predicted. Immediate expert cardiology review strongly advised.'
        };
      default:
        return {
          title: `${riskLevel} Priority`,
          color: 'bg-slate-50 text-slate-800 border-slate-200',
          badgeBg: 'bg-slate-600 text-white',
          icon: <AlertCircle className="w-6 h-6 text-slate-600" />,
          description: 'Evaluated by clinical decision support system.'
        };
    }
  };

  const config = getRiskConfig(riskLevel);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg flex flex-col justify-between h-full transition-colors">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Review Priority</span>
          <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${config.badgeBg}`}>
            {riskLevel} Priority
          </span>
        </div>

        <div className="flex items-center gap-3 mb-3">
          <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm">
            {config.icon}
          </div>
          <h4 className="text-lg font-bold text-slate-900 dark:text-white">{config.title}</h4>
        </div>

        <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-700/80 space-y-2">
          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
            {config.description}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 italic border-t border-slate-200 dark:border-slate-700 pt-2">
            Review priority reflects model uncertainty/secondary class scores and is not a clinical patient-risk score.
          </p>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>Model Triage Rank</span>
        <span className="font-bold text-slate-900 dark:text-white">{riskLevel} Priority</span>
      </div>
    </div>
  );
};
