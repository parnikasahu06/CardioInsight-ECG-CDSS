export interface ShapFeature {
  Feature: string;
  SHAP: number;
  AbsSHAP: number;
  clean_name?: string;
  direction?: 'positive' | 'negative' | string;
  interpretation?: string;
}

export type DiagnosticClass = 'NORM' | 'MI' | 'CD' | 'HYP' | 'STTC' | string;

export type RiskLevel = 'Low' | 'Medium' | 'High' | string;

export interface ProbabilitiesDict {
  [className: string]: number;
}

export interface SignalQuality {
  sqi_score: number;
  status: 'Excellent' | 'Acceptable' | 'Poor' | string;
  samples: number;
  n_leads: number;
  flatline_leads: string[];
  saturated_leads: string[];
  noisy_leads: string[];
}

export interface RecordInfo {
  record_id: string;
  timestamp: string;
  fs: number;
  duration_seconds: number;
  n_leads: number;
  hea_filename: string;
  dat_filename: string;
}

export interface WaveformData {
  leads: Record<string, number[]>;
  time: number[];
  fs: number;
}

export interface ClinicianReview {
  clinician_name: string;
  review_status: 'Confirmed & Agreed' | 'Disagreed / Alternative Diagnosis' | 'Additional Testing Required' | '';
  notes: string;
  review_date: string;
}

export interface ECGPredictionResponse {
  diagnosis: DiagnosticClass;
  confidence: number;
  risk_level: RiskLevel;
  recommendation: string;
  probabilities: ProbabilitiesDict;
  top_features: ShapFeature[];
  record_info?: RecordInfo;
  waveform_data?: WaveformData;
  signal_quality?: SignalQuality;
  clinical_evidence?: string[];
  review_guidance?: string[];
  clinical_warnings?: string[];
  disclaimer?: string;
  error?: string;
}

export interface UploadState {
  heaFile: File | null;
  datFile: File | null;
}

export const DIAGNOSIS_DETAILS: Record<string, { title: string; category: string; description: string; badgeColor: string }> = {
  NORM: {
    title: "Normal ECG (NORM)",
    category: "Normal Sinus Rhythm",
    description: "No significant clinical ECG abnormalities detected. Waveforms and intervals are within standard physiological reference ranges.",
    badgeColor: "bg-emerald-500/10 text-emerald-700 border-emerald-300"
  },
  MI: {
    title: "Myocardial Infarction (MI)",
    category: "Ischemic Heart Disease",
    description: "Features indicative of ischemic tissue damage or cardiac infarction detected. Urgently requires cardiology evaluation.",
    badgeColor: "bg-red-500/10 text-red-700 border-red-300"
  },
  CD: {
    title: "Conduction Disturbance (CD)",
    category: "Arrhythmia & Block",
    description: "Abnormalities in cardiac electrical impulse propagation observed (e.g. bundle branch blocks or AV delay).",
    badgeColor: "bg-amber-500/10 text-amber-700 border-amber-300"
  },
  HYP: {
    title: "Hypertrophy (HYP)",
    category: "Structural Abnormalities",
    description: "High wave voltage patterns consistent with left or right ventricular enlargement/hypertrophy.",
    badgeColor: "bg-purple-500/10 text-purple-700 border-purple-300"
  },
  STTC: {
    title: "ST/T Wave Abnormalities (STTC)",
    category: "Repolarization Variant",
    description: "ST elevation/depression or T-wave inversion observed, signaling potential myocardial ischemia or electrolyte shifts.",
    badgeColor: "bg-blue-500/10 text-blue-700 border-blue-300"
  }
};
