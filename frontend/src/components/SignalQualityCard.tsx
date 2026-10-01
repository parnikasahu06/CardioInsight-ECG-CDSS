'use client';

import React from 'react';
import { SignalQuality } from '@/types/ecg';
import { ShieldCheck, AlertTriangle, CheckCircle2, Activity } from 'lucide-react';

interface SignalQualityCardProps {
  signalQuality?: SignalQuality;
  recordInfo?: any;
}

export const SignalQualityCard: React.FC<SignalQualityCardProps> = ({ signalQuality, recordInfo }) => {
  const sqi_score = signalQuality?.sqi_score ?? 95.0;
  const status = signalQuality?.status ?? 'Acceptable';
  const n_leads = signalQuality?.n_leads ?? recordInfo?.n_leads ?? 12;
  const samples = signalQuality?.samples ?? (recordInfo ? Math.round(recordInfo.fs * recordInfo.duration_seconds) : 5000);
  const flatline_leads = signalQuality?.flatline_leads ?? [];
  const noisy_leads = signalQuality?.noisy_leads ?? [];
  const saturated_leads = signalQuality?.saturated_leads ?? [];
  const isHealthy = status === 'Excellent' || status === 'Acceptable';

  const extractedCount = recordInfo?.extracted_features_count ?? 322;
  const modelCount = recordInfo?.model_features_count ?? 274;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-4 transition-colors">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
            isHealthy ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300' : 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
          }`}>
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">ECG Record Summary & Signal Quality</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Record Verification & 12-Lead SQI Assessment</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
            isHealthy
              ? 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
              : 'bg-amber-50 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800'
          }`}>
            SQI Status: {status} ({sqi_score.toFixed(1)}%)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/80">
          <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Record Identifier</span>
          <span className="font-bold text-slate-900 dark:text-white text-sm font-mono">{recordInfo?.record_id || 'WFDB Record'}</span>
        </div>
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/80">
          <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Sampling / Duration</span>
          <span className="font-bold text-slate-900 dark:text-white text-sm">{recordInfo?.fs || 500} Hz ({recordInfo?.duration_seconds || 10.0}s)</span>
        </div>
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/80">
          <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Leads Analyzed</span>
          <span className="font-bold text-slate-900 dark:text-white text-sm">{n_leads} Leads</span>
        </div>
        <div className="bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/80">
          <span className="text-slate-500 dark:text-slate-400 block text-[11px]">Quality Index (SQI)</span>
          <span className="font-bold text-emerald-700 dark:text-emerald-400 text-sm flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            {sqi_score.toFixed(1)}% ({status})
          </span>
        </div>
      </div>

      {/* Feature Extraction Notice */}
      <div className="bg-sky-50/70 dark:bg-sky-950/50 border border-sky-200 dark:border-sky-800 rounded-xl p-3.5 text-xs text-sky-950 dark:text-sky-200 space-y-1">
        <div className="font-bold text-sky-900 dark:text-sky-100 flex items-center gap-2">
          <Activity className="w-4 h-4 text-sky-600 dark:text-sky-400" />
          <span>{extractedCount} ECG-Derived Features Extracted from Record</span>
        </div>
        <p className="text-[11px] text-sky-800 dark:text-sky-300 leading-relaxed">
          These {extractedCount} features ({modelCount} preprocessed features used for inference) are numerical measurements derived from the ECG signal (including P-QRS-T wave amplitudes, interval durations, lead voltage variances, and spectral power densities) used by the trained XGBoost model for classification.
        </p>
      </div>


      {/* Discovered Signal Warnings */}
      {((flatline_leads && flatline_leads.length > 0) ||
        (noisy_leads && noisy_leads.length > 0) ||
        (saturated_leads && saturated_leads.length > 0)) && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-900 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Signal Warnings Detected:</span>
          </div>
          {flatline_leads && flatline_leads.length > 0 && (
            <p>• Disconnected or Flatline Lead(s): {flatline_leads.join(', ')}</p>
          )}
          {noisy_leads && noisy_leads.length > 0 && (
            <p>• High Baseline Noise Lead(s): {noisy_leads.join(', ')}</p>
          )}
          {saturated_leads && saturated_leads.length > 0 && (
            <p>• Saturated Voltage Lead(s): {saturated_leads.join(', ')}</p>
          )}
        </div>
      )}
    </div>
  );
};
