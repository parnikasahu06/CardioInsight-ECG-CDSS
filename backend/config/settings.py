"""
=========================================================
Project Configuration & Clinical Mappings
ECG Clinical Decision Support System
=========================================================
Stores all project paths, global thresholds, medical
terminology definitions, and clinical disclaimers.
=========================================================
"""

import time
from pathlib import Path
from typing import Final

# -------------------------------------------------------
# System Metadata
# -------------------------------------------------------

API_VERSION: Final[str] = "1.0.0"
APP_NAME: Final[str] = "ECG Clinical Decision Support System"
START_TIME: Final[float] = time.time()

# -------------------------------------------------------
# Project Directories
# -------------------------------------------------------

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent.parent

MODEL_DIR: Final[Path] = PROJECT_ROOT / "models" / "trained"
UPLOAD_DIR: Final[Path] = PROJECT_ROOT / "uploads"
REPORT_DIR: Final[Path] = PROJECT_ROOT / "reports"

# -------------------------------------------------------
# Model Artifact Paths
# -------------------------------------------------------

MODEL_PATH: Final[Path] = MODEL_DIR / "final_xgboost_model.pkl"
SCALER_PATH: Final[Path] = MODEL_DIR / "standard_scaler.pkl"
IMPUTER_PATH: Final[Path] = MODEL_DIR / "median_imputer.pkl"
FEATURE_NAMES_PATH: Final[Path] = MODEL_DIR / "feature_names.csv"
CLASS_NAMES_PATH: Final[Path] = MODEL_DIR / "class_names.npy"

# -------------------------------------------------------
# Medical Terminology Mapping
# -------------------------------------------------------

MEDICAL_TERMINOLOGY: Final[dict[str, dict[str, str]]] = {
    "NORM": {
        "full_name": "Normal Sinus Rhythm",
        "category": "Physiological Baseline",
    },
    "MI": {
        "full_name": "Myocardial Infarction",
        "category": "Ischemic Heart Disease",
    },
    "CD": {
        "full_name": "Conduction Disturbance",
        "category": "Arrhythmia & Conduction Delay",
    },
    "HYP": {
        "full_name": "Ventricular Hypertrophy",
        "category": "Structural Cardiac Modification",
    },
    "STTC": {
        "full_name": "ST/T Wave Abnormalities",
        "category": "Repolarization Variant",
    },
}

# -------------------------------------------------------
# Clinical Recommendations Map
# -------------------------------------------------------

CLINICAL_RECOMMENDATIONS: Final[dict[str, str]] = {
    "NORM": "No significant ECG abnormalities detected. Routine clinical follow-up is recommended.",
    "MI": "Possible Myocardial Infarction detected. Immediate cardiology evaluation, 12-lead ECG review, and cardiac biomarker assessment (Troponin I/T) are recommended.",
    "CD": "Possible Conduction Disturbance detected. Clinical correlation and electrophysiology assessment are advised.",
    "HYP": "Possible Hypertrophy detected. Echocardiographic evaluation and blood pressure assessment are recommended.",
    "STTC": "ST/T abnormalities detected. Further ECG interpretation by a cardiologist is recommended to rule out acute ischemia.",
}

DEFAULT_RECOMMENDATION: Final[str] = "Consult a cardiologist for definitive clinical evaluation."

# -------------------------------------------------------
# CDSS Medical Disclaimer
# -------------------------------------------------------

MEDICAL_DISCLAIMER: Final[str] = (
    "This system is an AI-assisted Clinical Decision Support System (CDSS) intended solely "
    "to assist licensed healthcare professionals. It does not replace independent clinical evaluation "
    "or diagnostic judgment by a board-certified cardiologist."
)