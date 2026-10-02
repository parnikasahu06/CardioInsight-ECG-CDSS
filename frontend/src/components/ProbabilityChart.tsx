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
  LabelList
} from 'recharts';
import { ProbabilitiesDict } from '@/types/ecg';

interface ProbabilityChartProps {
  probabilities: ProbabilitiesDict;
  predictedDiagnosis: string;
}

const CLASS_COLOR_MAP: Record<string, string> = {
  NORM: '#10b981', // Emerald
  MI: '#ef4444',   // Red
  CD: '#f59e0b',   // Amber
  HYP: '#a855f7',  // Purple
  STTC: '#0284c7', // Blue
};

const CLASS_NAMES: Record<string, string> = {
  NORM: 'Normal (NORM)',
  MI: 'Myocardial Infarction (MI)',
  CD: 'Conduction Dist. (CD)',
  HYP: 'Hypertrophy (HYP)',
  STTC: 'ST/T Changes (STTC)',
};

export const ProbabilityChart: React.FC<ProbabilityChartProps> = ({ probabilities, predictedDiagnosis }) => {
  const chartData = Object.entries(probabilities || {}).map(([key, value]) => ({
    name: key,
    label: CLASS_NAMES[key] || key,
    probability: Number(value),
    color: CLASS_COLOR_MAP[key] || '#0284c7',
    isPredicted: key === predictedDiagnosis,
  }));

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg transition-colors">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Class Probability Distribution</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Predicted likelihood across 5 diagnostic classes (%)</p>
        </div>

        <div className="flex flex-wrap gap-2 text-xs">
          {Object.keys(CLASS_COLOR_MAP).map(cls => (
            <span
              key={cls}
              className={`px-2 py-0.5 rounded-md font-semibold text-[11px] ${
                cls === predictedDiagnosis ? 'ring-2 ring-slate-800 dark:ring-slate-200' : ''
              }`}
              style={{ backgroundColor: `${CLASS_COLOR_MAP[cls]}20`, color: CLASS_COLOR_MAP[cls] }}
            >
              {cls}
            </span>
          ))}
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.3} />
            <XAxis
              dataKey="name"
              tickLine={false}
              axisLine={{ stroke: '#64748b' }}
              tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
            />
            <YAxis
              domain={[0, 100]}
              tickLine={false}
              axisLine={{ stroke: '#64748b' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
              unit="%"
            />
            <Tooltip
              formatter={(value: number) => [`${value}%`, 'Probability']}
              labelFormatter={(label: string) => `Class: ${CLASS_NAMES[label] || label}`}
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)'
              }}
            />
            <Bar dataKey="probability" radius={[8, 8, 0, 0]} maxBarSize={55}>
              <LabelList dataKey="probability" position="top" formatter={(val: number) => `${val}%`} fill="#0284c7" fontSize={11} fontWeight={700} />
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke={entry.isPredicted ? '#38bdf8' : 'none'}
                  strokeWidth={entry.isPredicted ? 2 : 0}
                  opacity={entry.isPredicted ? 1 : 0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>XGBoost per-class probability</span>
        <span className="italic">These values represent model outputs and should not be interpreted as independently validated clinical probabilities.</span>
      </div>
    </div>
  );
};
