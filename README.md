# CardioInsight — Explainable AI-Based ECG Clinical Decision Support System

CardioInsight is an AI-assisted clinical decision-support system (CDSS) designed for analyzing 12-lead electrocardiogram (ECG) records from the PTB-XL dataset in standard WFDB format. The system integrates automated signal quality assessment, 213 extracted statistical ECG features, a multi-output XGBoost classification model, and SHAP-based feature explainability into an intuitive, clinician-centered decision-support workflow.

---

## Technical Overview

### Workflow Architecture

```
WFDB ECG Files (.hea + .dat)
   │
   ▼
Signal Quality & File Validation (SQI, Flatline/Noise Check, Stem Match)
   │
   ▼
12-Lead Signal Processing & Feature Extraction (213 Statistical ECG Features)
   │
   ▼
Preprocessing Pipeline (Median Imputation + Standard Scaling)
   │
   ▼
XGBoost Multi-Output Classification (Class Probabilities & Confidence %)
   │
   ▼
SHAP TreeExplainer (Feature Attribution & Directional Impact Vectors)
   │
   ▼
Non-Autonomous Clinical Decision-Support Interpretation
   │
   ▼
Clinician Review & Printable Clinical Report Export (PDF)
```

---

## Key Features

- **WFDB File Handling**: Drag-and-drop upload for paired WFDB header (`.hea`) and binary signal (`.dat`) files, with stem matching validation and sample record loading capability.
- **Interactive 12-Lead Waveform Visualizer**: High-resolution SVG rendering across all 12 leads (I, II, III, aVR, aVL, aVF, V1–V6) with selectable time windows (2.5s, 5.0s, 10.0s) and single-lead detailed tracing views.
- **Multi-Output AI Classification**: Multi-label evaluation across five core PTB-XL diagnostic categories with individual class probabilities and confidence scoring.
- **SHAP Feature Explainability**: Detailed feature-level explainability driven by `shap.TreeExplainer`, highlighting top positive and negative feature contributions.
- **Review Priority Assessment**: Transparent triage prioritization (`Low`, `Medium`, `High` Priority) reflecting model uncertainty and secondary class scores without replacing clinical judgment.
- **Clinician Review & Sign-Off**: Interface for physician notes, review status selection, and signature attribution.
- **Formal Clinical Report Generation**: Exportable PDF/printable report summarizing record metadata, SQI scores, model probabilities, SHAP attributions, clinical guidance, and clinician sign-off.
- **Theme Persistence**: Light and Dark clinical color palettes with single-icon toggle and `localStorage` state preservation.
- **Live System Monitoring**: Real-time backend API status badge monitoring model readiness and health endpoints.

---

## Input Requirements

CardioInsight requires paired WFDB format files belonging to the same record stem:

1. **Header File (`.hea`)**: Text file containing record metadata, sampling frequency ($f_s$), number of leads, recording duration, amplitude scaling, and lead names.
2. **Signal File (`.dat`)**: Binary file containing digital signal amplitudes recorded across all 12 ECG leads.

---

## Machine Learning Engine

- **Classifier**: Multi-output XGBoost Classifier (`models/trained/final_xgboost_model.pkl`)
- **Feature Pipeline**: 213 statistical and morphological ECG features extracted per lead (`models/trained/feature_names.csv`)
- **Preprocessing**: `SimpleImputer` (median strategy) + `StandardScaler` (`median_imputer.pkl`, `standard_scaler.pkl`)
- **Explainability**: `shap.TreeExplainer` computing exact feature contribution vectors
- **Supported Diagnostic Classes**:
  - `NORM` — Normal Sinus Rhythm
  - `MI` — Myocardial Infarction
  - `CD` — Conduction Disturbance
  - `HYP` — Ventricular Hypertrophy
  - `STTC` — ST/T-wave Abnormalities

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18, Tailwind CSS, Lucide React Icons
- **Language**: TypeScript

### Backend
- **Framework**: Python 3.10+, FastAPI, Uvicorn
- **Validation**: Pydantic v2
- **Data & Signal Processing**: NumPy, Pandas, SciPy, WFDB

### Machine Learning
- **Model**: XGBoost (`xgboost`)
- **Explainability**: SHAP (`shap`)
- **Preprocessing**: Scikit-learn (`scikit-learn`)

---

## Project Structure

```
ECG_Clinical_Decision_Support_System/
├── backend/
│   ├── api/
│   │   └── routes.py             # FastAPI endpoint definitions (/health, /predict)
│   ├── config/
│   │   ├── logging_config.py     # Application logger configuration
│   │   └── settings.py           # Backend settings & clinical descriptions
│   ├── middleware/
│   │   └── timing_middleware.py  # Processing execution timer
│   ├── schemas/
│   │   └── ecg_schemas.py        # Pydantic request/response payload schemas
│   ├── services/
│   │   ├── ecg_service.py        # Core service orchestrating processing & inference
│   │   ├── report_service.py     # Clinical report data assembler
│   │   └── signal_validator.py   # SQI calculation & flatline/noise detector
│   ├── feature_extractor.py      # 213 ECG feature extraction algorithm
│   ├── main.py                   # FastAPI app entry point & CORS configuration
│   ├── model_loader.py           # Trained model artifact loader
│   ├── predict.py                # Model prediction & guidance pipeline
│   ├── preprocessing.py          # Imputer & scaler preprocessor wrapper
│   ├── shap_explainer.py         # SHAP TreeExplainer attribution engine
│   └── utils.py                  # WFDB file parsing utilities
├── frontend/
│   ├── public/
│   │   └── samples/              # Sample WFDB records (00001_hr.hea, .dat)
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css       # Tailwind & custom CSS styles
│   │   │   ├── layout.tsx        # App root layout & metadata
│   │   │   └── page.tsx          # Main application page
│   │   ├── components/           # UI components (Header, Sidebar, WaveformViewer, etc.)
│   │   ├── lib/
│   │   │   └── api.ts            # Frontend API client
│   │   └── types/
│   │       └── ecg.ts            # TypeScript interfaces
│   ├── package.json
│   └── tailwind.config.js
├── models/
│   └── trained/                  # Trained ML artifacts (.pkl, .npy, .csv)
├── requirements.txt              # Backend Python dependencies
└── README.md
```

---

## Local Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

---

### 1. Backend Setup

1. **Navigate to project root**:
   ```bash
   cd ECG_Clinical_Decision_Support_System
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI backend server**:
   ```bash
   $env:PYTHONPATH="."
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
   The backend API will be running at `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

1. **Navigate to the frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the Next.js development server**:
   ```bash
   npm run dev
   ```
   The application UI will be accessible at `http://localhost:3000`.

---

## Usage Guide

1. **Access the Dashboard**: Open `http://localhost:3000` in your web browser. Verify the **Backend** status badge indicates `Backend Online`.
2. **Upload ECG Files**:
   - Navigate to **Upload ECG** from the sidebar or click **Upload ECG Record →**.
   - Drag and drop or select a matching WFDB header (`.hea`) and binary signal (`.dat`) file pair, or click **Load Sample WFDB Record**.
3. **Analyze ECG**: Click **Analyze ECG**. The system validates signal quality, extracts features, runs XGBoost inference, and computes SHAP values.
4. **Inspect Signal Waveforms**: View full 12-lead ECG tracings under **ECG Waveform**, switch between leads, adjust window duration, or expand individual lead detailed views.
5. **Review AI Explanations**: Inspect top positive and negative feature attributions under **AI Explanation** to understand how extracted parameters influenced model output.
6. **Complete Clinical Review**: Input clinician name/ID, select a review decision status, and record evaluation notes under **Clinical Review**.
7. **Export Clinical Report**: Click **Print / Download PDF** under **Report** to generate a printable medical summary.

---

## Important Clinical Disclaimer

> **CARDIOINSIGHT IS AN ACADEMIC RESEARCH AND DECISION-SUPPORT PROTOTYPE.**
>
> CardioInsight is intended solely to assist licensed healthcare professionals as a secondary decision-support tool. It **does not** provide autonomous medical diagnoses, treatment recommendations, or definitive clinical findings. Final diagnostic interpretation must always be conducted by a board-certified cardiologist or qualified physician correlating AI findings with patient history, clinical presentation, and comprehensive diagnostic evaluation.

---

## System Limitations

- **Format Specificity**: Designed specifically for 12-lead PTB-XL ECG records in standard WFDB paired header (`.hea`) and binary signal (`.dat`) format.
- **Dataset Context**: Feature extraction and trained model weights reflect the distribution of the PTB-XL clinical database.
- **Decision Support Scope**: Model output priority scores reflect mathematical uncertainty and class probabilities rather than absolute patient risk.
