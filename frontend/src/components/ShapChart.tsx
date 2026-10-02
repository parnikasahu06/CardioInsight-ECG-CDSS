'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from 'recharts';
import { ShapFeature } from '@/types/ecg';
import { HelpCircle, Layers } from 'lucide-react';

interface ShapChartProps {
  topFeatures: ShapFeature[];
  predictedDiagnosis: string;
  decisionStatus?: string;
}

export const ShapChart: React.FC<ShapChartProps> = ({ topFeatures, predictedDiagnosis, decisionStatus }) => {
  if (!topFeatures || topFeatures.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg text-center text-slate-500 text-sm">
        No SHAP feature importances available for this record.
      </div>
    );
  }

  const chartData = topFeatures.map(item => ({
    name: item.Feature,
    cleanName: item.Feature.replace(/_/g, ' ').toUpperCase(),
    shap: Number(item.SHAP),
    absShap: Number(item.AbsSHAP),
    isPositive: Number(item.SHAP) >= 0,
  }));

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg transition-colors">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-600 dark:text-sky-400" />
            <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">SHAP Feature Importance</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {decisionStatus === 'no_class_above_threshold' ? (
              <>Features driving the highest-scoring class (below decision threshold): <span className="font-semibold text-slate-700 dark:text-slate-300">{predictedDiagnosis}</span></>
            ) : (
              <>Top ECG parameters driving model decision for <span className="font-semibold text-slate-700 dark:text-slate-300">{predictedDiagnosis}</span></>
            )}
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5 text-sky-700 dark:text-sky-300">
            <span className="w-3 h-3 rounded-sm bg-sky-500 inline-block"></span>
            <span>Positive Driver (+ SHAP)</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
            <span className="w-3 h-3 rounded-sm bg-slate-400 dark:bg-slate-600 inline-block"></span>
            <span>Negative Driver (- SHAP)</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={chartData}
            margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" opacity={0.3} />
            <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="name"
              stroke="#64748b"
              tick={{ fontSize: 11, fontWeight: 600, fill: '#94a3b8' }}
              width={95}
            />
            <Tooltip
              formatter={(value: number) => [value.toFixed(4), 'SHAP Value']}
              labelFormatter={(label: string) => `Feature: ${label}`}
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
              }}
            />
            <ReferenceLine x={0} stroke="#94a3b8" strokeDasharray="3 3" />
            <Bar dataKey="shap" radius={[0, 6, 6, 0]} maxBarSize={28}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`shap-cell-${index}`}
                  fill={entry.isPositive ? '#0284c7' : '#64748b'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Feature explanation table summary */}
      <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-3">
        <div className="bg-sky-50/60 dark:bg-sky-950/50 border border-sky-200 dark:border-sky-800 rounded-xl p-3 text-xs text-sky-950 dark:text-sky-200 flex items-start gap-2">
          <HelpCircle className="w-4 h-4 text-sky-600 dark:text-sky-400 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] leading-relaxed">
            <strong>SHAP Feature Contribution:</strong> SHAP values describe how individual extracted ECG features influenced the model prediction. They do not independently establish a clinical diagnosis.
          </p>
        </div>

        <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Top Driving Features Attribution</h4>
        <div className="space-y-2">
          {topFeatures.map((item, idx) => {
            const isPos = Number(item.SHAP) >= 0;
            return (
              <div key={idx} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 dark:text-white">{item.clean_name || item.Feature}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                      SHAP: {item.SHAP >= 0 ? `+${item.SHAP.toFixed(4)}` : item.SHAP.toFixed(4)}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      isPos ? 'bg-sky-100 dark:bg-sky-950 text-sky-800 dark:text-sky-300 border border-sky-200 dark:border-sky-800' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                    }`}>
                      {isPos ? 'Positive Impact (+)' : 'Negative Impact (-)'}
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-600 dark:text-slate-400">
                  {isPos
                    ? `Positive contribution: This feature pushed the model toward the predicted class (${predictedDiagnosis}).`
                    : `Negative contribution: This feature pushed the model away from the predicted class (${predictedDiagnosis}).`}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
