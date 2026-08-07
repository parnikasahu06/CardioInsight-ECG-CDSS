'use client';

import React from 'react';
import { Stethoscope, CheckSquare, Info, ShieldAlert, FileText } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: string;
  evidence?: string[];
  guidance?: string[];
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  evidence,
  guidance,
}) => {
  return (
    <div className="bg-gradient-to-br from-slate-900 to-sky-950 text-white rounded-2xl p-6 shadow-xl border border-slate-800 relative overflow-hidden space-y-5">
      {/* Background ECG watermark */}
      <div className="absolute right-[-20px] bottom-[-20px] opacity-10 pointer-events-none">
        <Stethoscope className="w-48 h-48 text-sky-400" />
      </div>

      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-sky-500/20 text-sky-300 flex items-center justify-center border border-sky-400/30 shadow-inner">
            <Stethoscope className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-white tracking-tight">Clinical Decision Support & Interpretation</h3>
            <p className="text-xs text-slate-400">Non-autonomous medical decision assistance guidance</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-sky-400/10 text-sky-300 border border-sky-400/20">
          Advisory Protocol
        </span>
      </div>

      {/* Model Interpretation */}
      <div className="relative z-10 bg-slate-800/80 backdrop-blur-md p-4 rounded-xl border border-slate-700/80 space-y-1">
        <span className="text-[11px] font-bold uppercase tracking-wider text-sky-400">Summary Interpretation</span>
        <p className="text-sm text-slate-100 leading-relaxed font-medium">
          "{recommendation}"
        </p>
      </div>

      {/* Model Derived Evidence & Guidance Grid */}
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Supporting Evidence */}
        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/50 space-y-2">
          <div className="flex items-center gap-2 font-bold text-sky-300">
            <FileText className="w-4 h-4 text-sky-400" />
            <span>Model-Derived ECG Evidence</span>
          </div>
          {evidence && evidence.length > 0 ? (
            <ul className="space-y-1.5 text-slate-300 text-[11px] list-disc list-inside">
              {evidence.map((item, idx) => (
                <li key={idx} className="leading-relaxed">{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-400 text-[11px]">Primary feature attributions support diagnostic classification.</p>
          )}
        </div>

        {/* Clinician Review Guidance */}
        <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/50 space-y-2">
          <div className="flex items-center gap-2 font-bold text-emerald-300">
            <CheckSquare className="w-4 h-4 text-emerald-400" />
            <span>Clinician Review Guidance</span>
          </div>
          {guidance && guidance.length > 0 ? (
            <ul className="space-y-1.5 text-slate-300 text-[11px] list-disc list-inside">
              {guidance.map((item, idx) => (
                <li key={idx} className="leading-relaxed">{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-400 text-[11px]">Perform standard clinical correlation with patient history.</p>
          )}
        </div>
      </div>

      {/* Non-Autonomous Notice */}
      <div className="relative z-10 flex items-center gap-2 text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
        <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span>Decision support assists clinical evaluation. It does not replace clinician judgment or prescribe treatments autonomously.</span>
      </div>
    </div>
  );
};

