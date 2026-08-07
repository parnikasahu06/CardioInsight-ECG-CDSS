'use client';

import React, { useState } from 'react';
import { WaveformData, RecordInfo } from '@/types/ecg';
import { Activity, ZoomIn, Grid, Maximize2, RefreshCw } from 'lucide-react';

interface WaveformViewerProps {
  waveformData?: WaveformData;
  recordInfo?: RecordInfo;
}

export const WaveformViewer: React.FC<WaveformViewerProps> = ({ waveformData, recordInfo }) => {
  const [selectedLead, setSelectedLead] = useState<string>('All');
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [timeWindow, setTimeWindow] = useState<number>(10); // seconds to display

  if (!waveformData || !waveformData.leads || Object.keys(waveformData.leads).length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-md text-center text-slate-500">
        <Activity className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <p className="text-sm font-medium">Waveform data unavailable for this record.</p>
      </div>
    );
  }

  const leads = Object.keys(waveformData.leads);
  const timePoints = waveformData.time || [];
  const maxTime = timePoints.length > 0 ? timePoints[timePoints.length - 1] : 10;

  // Helper to render an SVG path for a given lead's signal array
  const renderLeadSVG = (leadName: string, height: number = 100, width: number = 800) => {
    const signal = waveformData.leads[leadName];
    if (!signal || signal.length === 0) return null;

    // Filter points based on zoom / time window
    const visiblePointsCount = Math.min(signal.length, Math.round((signal.length * timeWindow) / (maxTime || 10)));
    const slicedSignal = signal.slice(0, visiblePointsCount);
    const n = slicedSignal.length;

    // Dynamic amplitude scaling
    let maxAbs = 0.5;
    for (let i = 0; i < n; i++) {
      const absVal = Math.abs(slicedSignal[i]);
      if (absVal > maxAbs) maxAbs = absVal;
    }

    const padding = 15;
    const availableHeight = height - padding * 2;
    const centerY = height / 2;
    const scaleY = (availableHeight / 2) / (maxAbs || 1);

    const pathPoints = slicedSignal.map((val, idx) => {
      const x = (idx / (n - 1)) * width;
      const y = centerY - val * scaleY;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    const pathData = `M ${pathPoints.join(' L ')}`;

    return (
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-full overflow-visible"
        preserveAspectRatio="none"
      >
        {/* ECG Grid Lines (Medical Grid Effect) */}
        <defs>
          <pattern id={`ecgGrid-${leadName}`} width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#fecdd3" strokeWidth="0.5" opacity="0.6" />
            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#fda4af" strokeWidth="1" opacity="0.8" />
          </pattern>
        </defs>
        <rect width={width} height={height} fill={`url(#ecgGrid-${leadName})`} />

        {/* Baseline (0 mV) */}
        <line x1="0" y1={centerY} x2={width} y2={centerY} stroke="#f43f5e" strokeWidth="0.75" strokeDasharray="4 4" opacity="0.4" />

        {/* Waveform Signal Line */}
        <path
          d={pathData}
          fill="none"
          stroke="#0284c7"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden transition-colors">
      {/* Header Bar */}
      <div className="p-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-sky-600 text-white flex items-center justify-center shadow-md">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">12-Lead ECG Signal Waveforms</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Real WFDB signal data ({recordInfo?.fs || waveformData.fs} Hz • {recordInfo?.duration_seconds || maxTime}s duration)
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          {/* Lead Filter Tabs */}
          <div className="flex items-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-1 shadow-sm overflow-x-auto max-w-full">
            <button
              onClick={() => setSelectedLead('All')}
              className={`px-3 py-1 rounded-lg font-semibold transition-colors ${
                selectedLead === 'All'
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
              }`}
            >
              12-Lead Grid
            </button>
            {leads.map((lead) => (
              <button
                key={lead}
                onClick={() => setSelectedLead(lead)}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                  selectedLead === lead
                    ? 'bg-sky-600 text-white shadow-sm'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                }`}
              >
                {lead}
              </button>
            ))}
          </div>

          {/* Time Window Select */}
          <div className="flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-1 shadow-sm">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Window:</span>
            <select
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="bg-transparent font-bold text-slate-900 dark:text-white focus:outline-none cursor-pointer"
            >
              <option value={2.5} className="dark:bg-slate-900">2.5 sec</option>
              <option value={5} className="dark:bg-slate-900">5.0 sec</option>
              <option value={10} className="dark:bg-slate-900">Full ({maxTime}s)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid or Single Lead View */}
      <div className="p-6 bg-rose-50/20 dark:bg-slate-950/40">
        {selectedLead === 'All' ? (
          /* 12-Lead Grid Layout */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {leads.map((lead) => (
              <div
                key={lead}
                className="bg-white dark:bg-slate-900 rounded-xl border border-rose-200/80 dark:border-slate-800 shadow-sm p-3 hover:border-sky-400 dark:hover:border-sky-500 transition-all group"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-black tracking-wider text-rose-700 dark:text-rose-400 bg-rose-100 dark:bg-rose-950/80 border border-rose-200 dark:border-rose-800 px-2 py-0.5 rounded-md uppercase">
                    Lead {lead}
                  </span>
                  <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">0 - {timeWindow}s</span>
                </div>
                <div className="h-28 rounded-lg overflow-hidden bg-rose-50/30 dark:bg-slate-950 border border-rose-100 dark:border-slate-800 relative">
                  {renderLeadSVG(lead, 110, 400)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Single Selected Lead Detailed View */
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-rose-200 dark:border-slate-800 p-5 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-black text-rose-700 dark:text-rose-400 bg-rose-100 dark:bg-rose-950/80 border border-rose-300 dark:border-rose-800 px-3 py-1 rounded-lg uppercase">
                  Lead {selectedLead} — High Resolution Tracing
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  Amplitude Scale: ±1 mV • Baseline: 0 mV
                </span>
              </div>
              <button
                onClick={() => setSelectedLead('All')}
                className="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:text-sky-800 flex items-center gap-1"
              >
                <Grid className="w-3.5 h-3.5" />
                Back to 12-Lead Grid
              </button>
            </div>

            <div className="h-64 rounded-xl overflow-hidden bg-rose-50/40 dark:bg-slate-950 border border-rose-200 dark:border-slate-800 relative p-2">
              {renderLeadSVG(selectedLead, 240, 1000)}
            </div>

            {/* Axes labels */}
            <div className="flex items-center justify-between text-xs font-mono text-slate-500 dark:text-slate-400 px-2">
              <span>Time: 0.0s</span>
              <span>Time: {(timeWindow / 2).toFixed(1)}s</span>
              <span>Time: {timeWindow.toFixed(1)}s</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="px-6 py-3 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            Standard Grid: 25 mm/s, 10 mm/mV
          </span>
          <span>Lead Count: {leads.length}</span>
        </div>
        <span>Click any lead tab for expanded single-lead tracing</span>
      </div>
    </div>
  );
};
