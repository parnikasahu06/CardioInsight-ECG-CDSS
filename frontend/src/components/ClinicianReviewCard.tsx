'use client';

import React from 'react';
import { ClinicianReview } from '@/types/ecg';
import { UserCheck, FileText, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface ClinicianReviewCardProps {
  review: ClinicianReview;
  onChange: (updated: ClinicianReview) => void;
}

export const ClinicianReviewCard: React.FC<ClinicianReviewCardProps> = ({ review, onChange }) => {
  const handleStatusChange = (status: ClinicianReview['review_status']) => {
    onChange({ ...review, review_status: status });
  };

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange({ ...review, notes: e.target.value });
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...review, clinician_name: e.target.value });
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg space-y-6 transition-colors">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-md">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Clinician Review & Verification</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Attending Physician Interpretation & Sign-off
            </p>
          </div>
        </div>

        <span className="text-xs bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 px-3 py-1 rounded-full font-bold">
          Required for Final Diagnosis
        </span>
      </div>

      {/* Review Decision Buttons */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
          Clinical Verification Status
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            type="button"
            onClick={() => handleStatusChange('Confirmed & Agreed')}
            className={`flex items-center gap-2 p-3.5 rounded-xl border text-xs font-bold transition-all ${
              review.review_status === 'Confirmed & Agreed'
                ? 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-200 border-emerald-500 ring-2 ring-emerald-500/20 shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
            }`}
          >
            <CheckCircle2 className={`w-4 h-4 ${review.review_status === 'Confirmed & Agreed' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`} />
            <span>Confirmed & Agreed</span>
          </button>

          <button
            type="button"
            onClick={() => handleStatusChange('Disagreed / Alternative Diagnosis')}
            className={`flex items-center gap-2 p-3.5 rounded-xl border text-xs font-bold transition-all ${
              review.review_status === 'Disagreed / Alternative Diagnosis'
                ? 'bg-red-50 dark:bg-red-950/80 text-red-800 dark:text-red-200 border-red-500 ring-2 ring-red-500/20 shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
            }`}
          >
            <AlertTriangle className={`w-4 h-4 ${review.review_status === 'Disagreed / Alternative Diagnosis' ? 'text-red-600 dark:text-red-400' : 'text-slate-400'}`} />
            <span>Disagreed / Alternative</span>
          </button>

          <button
            type="button"
            onClick={() => handleStatusChange('Additional Testing Required')}
            className={`flex items-center gap-2 p-3.5 rounded-xl border text-xs font-bold transition-all ${
              review.review_status === 'Additional Testing Required'
                ? 'bg-amber-50 dark:bg-amber-950/80 text-amber-800 dark:text-amber-200 border-amber-500 ring-2 ring-amber-500/20 shadow-sm'
                : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
            }`}
          >
            <HelpCircle className={`w-4 h-4 ${review.review_status === 'Additional Testing Required' ? 'text-amber-600 dark:text-amber-400' : 'text-slate-400'}`} />
            <span>Additional Testing</span>
          </button>
        </div>
      </div>

      {/* Clinician Notes Field */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
          Clinician Interpretation & Findings
        </label>
        <textarea
          rows={3}
          value={review.notes}
          onChange={handleNotesChange}
          placeholder="Enter physical examination notes, serial ECG comparison, or alternative clinical diagnostic impressions..."
          className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 p-3.5 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-sky-500 focus:border-sky-500 shadow-inner placeholder:text-slate-400 dark:placeholder:text-slate-500"
        />
      </div>

      {/* Physician Name & Date Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Evaluating Clinician Name / ID</label>
          <input
            type="text"
            value={review.clinician_name}
            onChange={handleNameChange}
            placeholder="Enter Clinician Name / ID"
            className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
          />
        </div>
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Review Date & Timestamp</label>
          <input
            type="text"
            readOnly
            value={review.review_date || new Date().toLocaleString()}
            className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2 text-xs text-slate-600 dark:text-slate-300 font-mono"
          />
        </div>
      </div>

      <div className="bg-emerald-50/70 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 rounded-xl p-3 text-xs text-emerald-950 dark:text-emerald-200 text-center font-medium">
        AI output is intended to support, not replace, clinical judgment.
      </div>
    </div>
  );
};
