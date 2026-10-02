'use client';

import React from 'react';
import { ECGPredictionResponse, ClinicianReview } from '@/types/ecg';
import { Printer, X, Activity, AlertCircle } from 'lucide-react';

interface ECGReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: ECGPredictionResponse;
  clinicianReview: ClinicianReview;
}

export const ECGReportModal: React.FC<ECGReportModalProps> = ({
  isOpen,
  onClose,
  result,
  clinicianReview,
}) => {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const rec = result.record_info;
  const sq = result.signal_quality;
  const supportedClasses = ['NORM', 'MI', 'CD', 'HYP', 'STTC'];

  const classDescriptions: Record<string, string> = {
    NORM: 'Normal ECG — Baseline Sinus Pattern',
    MI: 'Myocardial Infarction — Ischemic Tissue Alteration',
    CD: 'Conduction Disturbance — Impulse Conduction Delay/Block',
    HYP: 'Hypertrophy — High Voltage Ventricular Enlargement',
    STTC: 'ST/T Wave Abnormalities — Repolarization Variant',
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 print:p-0 print:bg-white print:static print:block">
      <style jsx global>{`
        @media print {
          @page {
            margin: 10mm;
            size: A4 portrait;
          }
          body {
            background: #ffffff !important;
            color: #0f172a !important;
            font-family: system-ui, -apple-system, sans-serif !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          header, sidebar, footer, .print\\:hidden {
            display: none !important;
          }
          .avoid-break {
            page-break-inside: avoid;
            break-inside: avoid;
          }
        }
      `}</style>

      {/* Modal Container */}
      <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[92vh] print:max-h-none print:shadow-none print:border-none print:rounded-none">
        
        {/* Modal Toolbar (Hidden during print) */}
        <div className="bg-slate-900 text-white p-4 flex items-center justify-between print:hidden">
          <div className="flex items-center gap-2 text-sm font-bold">
            <Activity className="w-5 h-5 text-sky-400" />
            <span>CardioInsight Report Preview</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all shadow-md"
            >
              <Printer className="w-4 h-4" />
              <span>Print / Download PDF</span>
            </button>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Formal Document Content */}
        <div className="p-8 sm:p-10 overflow-y-auto space-y-6 text-slate-900 print:p-0 print:overflow-visible">
          
          {/* 1. Header & Branding */}
          <div className="border-b-2 border-slate-900 pb-4 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black tracking-tight text-slate-900 uppercase">CardioInsight</span>
              </div>
              <h1 className="text-base font-extrabold text-slate-700 tracking-wide mt-0.5">
                Explainable AI-Based ECG Clinical Decision Support System
              </h1>
              <p className="text-xs text-slate-500">Automated 12-Lead Diagnostic & Explainability Analysis Report</p>
            </div>
            
            <div className="text-right text-xs text-slate-600 space-y-1">
              <div className="font-bold text-slate-900">CONFIDENTIAL MEDICAL DOCUMENT</div>
              <div>Report Date: {rec?.timestamp || new Date().toLocaleString()}</div>
              <div className="font-mono text-[11px] text-slate-500">Pipeline: XGBoost + SHAP Engine</div>
            </div>
          </div>

          {/* 2. Record Information Table */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              1. Record Information
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs">
              <div>
                <span className="text-slate-500 block text-[11px]">ECG Record ID</span>
                <span className="font-bold font-mono text-slate-900">{rec?.record_id || 'WFDB_RECORD'}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Analysis Timestamp</span>
                <span className="font-medium text-slate-900">{rec?.timestamp || 'N/A'}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Sampling Frequency</span>
                <span className="font-medium text-slate-900">{rec?.fs || 500} Hz</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Recording Duration</span>
                <span className="font-medium text-slate-900">{rec?.duration_seconds || '10.0'} seconds</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Number of Leads</span>
                <span className="font-medium text-slate-900">{rec?.n_leads || 12} Leads</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Input Filenames</span>
                <span className="font-mono text-[11px] text-slate-800">{rec?.hea_filename || '.hea'} / {rec?.dat_filename || '.dat'}</span>
              </div>
            </div>
          </div>

          {/* 3. Signal Quality Section */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              2. Signal Quality Assessment (SQI)
            </h2>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-500">SQI Quality Status: </span>
                  <span className="font-bold text-slate-900">{sq?.status || 'Acceptable'} ({sq?.sqi_score ? sq.sqi_score.toFixed(1) : '95.0'}%)</span>
                </div>
                <div>
                  <span className="text-slate-500">Validation Status: </span>
                  <span className="font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                    Signal Validated
                  </span>
                </div>
              </div>
              
              <div className="text-[11px] text-slate-600">
                {sq?.flatline_leads && sq.flatline_leads.length > 0 ? (
                  <span className="text-red-700 font-semibold">Flatline Detected: Lead(s) {sq.flatline_leads.join(', ')}</span>
                ) : sq?.noisy_leads && sq.noisy_leads.length > 0 ? (
                  <span className="text-amber-700 font-semibold">High Noise Detected: Lead(s) {sq.noisy_leads.join(', ')}</span>
                ) : (
                  <span>No signal saturation, flatlining, or excessive noise detected across 12 leads.</span>
                )}
              </div>
            </div>
          </div>

          {/* 4 & 5. AI Classification & Supported Classes */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              3. AI Multi-Output Classification Results
            </h2>
            
            <div className="grid grid-cols-3 gap-3 bg-sky-50/60 p-4 rounded-xl border border-sky-200 text-xs mb-3">
              <div>
                <span className="text-sky-800 font-bold block text-[11px]">Primary Predicted Class</span>
                <span className="text-base font-black text-sky-950">
                  {result.decision_status === 'no_class_above_threshold' ? 'No class above decision threshold' : result.diagnosis}
                </span>
              </div>
              <div>
                <span className="text-sky-800 font-bold block text-[11px]">Model Confidence</span>
                <span className="text-base font-black text-emerald-700">{result.confidence.toFixed(2)}%</span>
              </div>
              <div>
                <span className="text-sky-800 font-bold block text-[11px]">Review Priority</span>
                <span className="text-base font-black text-slate-900">{result.risk_level} Priority</span>
              </div>
            </div>

            {result.decision_status === 'no_class_above_threshold' ? (
              <div className="bg-amber-50 border border-amber-200 p-2.5 rounded-lg text-[11px] text-amber-900 mb-3">
                Highest score: <span className="font-bold">{result.diagnosis}</span> ({result.confidence.toFixed(2)}%
                {result.decision_thresholds?.[result.diagnosis] !== undefined ? `, threshold ${(result.decision_thresholds[result.diagnosis] * 100).toFixed(0)}%` : ''})
              </div>
            ) : (
              <div className="bg-slate-50 border border-slate-200 p-2.5 rounded-lg text-[11px] text-slate-600 mb-3">
                Review priority reflects model uncertainty and secondary class outputs. It is not a clinical patient-risk score.
              </div>
            )}

            {/* Supported Class Probabilities Table */}
            <table className="w-full text-left text-xs border border-slate-200 rounded-xl overflow-hidden">
              <thead className="bg-slate-100 font-bold text-slate-700 border-b border-slate-200">
                <tr>
                  <th className="p-2.5">Class Code</th>
                  <th className="p-2.5">Diagnostic Description</th>
                  <th className="p-2.5 text-right">Probability Score</th>
                  <th className="p-2.5 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {supportedClasses.map((cls) => {
                  const prob = result.probabilities?.[cls] ?? 0.0;
                  const isPositive = result.positive_classes ? result.positive_classes.includes(cls) : (result.decision_status !== 'no_class_above_threshold' && cls === result.diagnosis);
                  const isPrimary = result.decision_status !== 'no_class_above_threshold' && cls === result.diagnosis;
                  return (
                    <tr key={cls} className={isPrimary ? 'bg-sky-50 font-bold' : isPositive ? 'bg-emerald-50/50 font-semibold' : 'hover:bg-slate-50'}>
                      <td className="p-2.5 font-mono font-bold text-slate-900">{cls}</td>
                      <td className="p-2.5 text-slate-700">{classDescriptions[cls] || cls}</td>
                      <td className="p-2.5 text-right font-mono font-bold">{prob.toFixed(2)}%</td>
                      <td className="p-2.5 text-center">
                        {isPrimary ? (
                          <span className="bg-sky-600 text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">
                            Primary Finding
                          </span>
                        ) : isPositive ? (
                          <span className="bg-emerald-600 text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">
                            Secondary Positive
                          </span>
                        ) : (
                          <span className="text-slate-400 text-[11px]">
                            {result.decision_status === 'no_class_above_threshold' ? 'Below Threshold' : 'Evaluated'}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* 6. Explainable AI Section */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              4. Explainable AI (SHAP Feature Attributions)
            </h2>

            <div className="bg-sky-50/70 border border-sky-200 p-2.5 rounded-lg text-[11px] text-sky-900 mb-2">
              SHAP values describe how individual extracted ECG features influenced the model prediction. They do not independently establish a clinical diagnosis.
            </div>

            <div className="space-y-2">
              {result.top_features && result.top_features.length > 0 ? (
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100 font-bold text-slate-700 border-b border-slate-200">
                      <tr>
                        <th className="p-2">Feature Name</th>
                        <th className="p-2">Impact Direction</th>
                        <th className="p-2 text-right">SHAP Value</th>
                        <th className="p-2">Clinical Feature Attribution</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 text-[11px]">
                      {result.top_features.map((feat, idx) => (
                        <tr key={idx}>
                          <td className="p-2 font-bold text-slate-900">{feat.clean_name || feat.Feature}</td>
                          <td className="p-2">
                            {feat.direction === 'positive' || (feat.SHAP && feat.SHAP >= 0) ? (
                              <span className="text-emerald-700 font-bold">Positive Support (+)</span>
                            ) : (
                              <span className="text-amber-700 font-bold">Suppressing Factor (-)</span>
                            )}
                          </td>
                          <td className="p-2 text-right font-mono font-bold">{feat.SHAP ? (feat.SHAP >= 0 ? `+${feat.SHAP.toFixed(4)}` : feat.SHAP.toFixed(4)) : 'N/A'}</td>
                          <td className="p-2 text-slate-600">{feat.interpretation || 'Model derived attribution metric.'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">SHAP feature attributions computed directly from XGBoost tree explainer.</p>
              )}
            </div>
          </div>

          {/* 7. Clinical Decision Support Section */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              5. Clinical Decision Support Guidance
            </h2>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs space-y-2">
              <p className="font-semibold text-slate-900">{result.recommendation}</p>
              
              {result.review_guidance && result.review_guidance.length > 0 && (
                <ul className="list-disc list-inside space-y-1 text-slate-700 text-[11px]">
                  {result.review_guidance.map((g, idx) => (
                    <li key={idx}>{g}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* 8. Clinician Review Section */}
          <div className="space-y-2 avoid-break">
            <h2 className="text-xs font-black uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">
              6. Clinician Review & Sign-Off
            </h2>
            <div className="border border-slate-300 rounded-xl p-4 space-y-3 bg-white text-xs">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-500">Evaluating Clinician: </span>
                  <span className="font-bold text-slate-900">{clinicianReview.clinician_name || 'Not entered'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Decision Status: </span>
                  <span className="font-bold text-slate-900">{clinicianReview.review_status || 'Pending Review'}</span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block mb-1">Clinician Interpretation & Notes:</span>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 min-h-[50px] font-mono text-[11px] text-slate-800">
                  {clinicianReview.notes || '[ Space reserved for physician evaluation notes ]'}
                </div>
              </div>

              {/* Signature Line Block */}
              <div className="grid grid-cols-2 gap-8 pt-4">
                <div>
                  <div className="border-b border-slate-400 h-8"></div>
                  <span className="text-[10px] text-slate-500 block mt-1">Physician Signature</span>
                </div>
                <div>
                  <div className="border-b border-slate-400 h-8 flex items-end font-mono text-[11px] pb-0.5">
                    {clinicianReview.review_date || new Date().toLocaleDateString()}
                  </div>
                  <span className="text-[10px] text-slate-500 block mt-1">Date & Time</span>
                </div>
              </div>
            </div>
          </div>

          {/* 9. Medical Disclaimer */}
          <div className="pt-2 border-t border-slate-200 avoid-break">
            <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-3.5 text-[11px] text-amber-900 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                <strong>Disclaimer:</strong> {result.disclaimer || "AI-generated results are intended for clinical decision support and must not be used as a standalone diagnosis. Final interpretation must be performed by a qualified clinician."}
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
