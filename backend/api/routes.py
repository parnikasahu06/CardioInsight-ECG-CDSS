"""
=========================================================
API Routes & Production Endpoints - v5 Pipeline
ECG Clinical Decision Support System
=========================================================
Handles REST API endpoints for ECG classification:
    - GET /: Application Metadata
    - GET /health: Health Check & System Uptime
    - POST /predict: 12-Lead WFDB ECG Record Classification
=========================================================
"""

import threading
import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from backend.config.logging_config import setup_logger
from backend.config.settings import API_VERSION, APP_NAME, START_TIME
from backend.feature_extractor import FeatureExtractor
from backend.predict import ECGPredictor
from backend.schemas.ecg_schemas import (
    ECGPredictionResponseModel,
    HealthResponseModel,
    HomeResponseModel,
)
from backend.services.ecg_service import ECGFileService
from backend.services.signal_validator import ECGSignalValidator

logger = setup_logger("api_routes")
router = APIRouter(tags=["ECG Clinical Decision Support"])

# --------------------------------------------------------
# Thread-safe Singleton Instances & FastAPI Dependencies
# --------------------------------------------------------

_extractor: FeatureExtractor | None = None
_predictor: ECGPredictor | None = None
_lock = threading.Lock()


def get_feature_extractor() -> FeatureExtractor:
    """FastAPI Dependency: Lazy-load and return FeatureExtractor singleton."""
    global _extractor
    if _extractor is None:
        with _lock:
            if _extractor is None:
                logger.info("Initializing FeatureExtractor singleton...")
                _extractor = FeatureExtractor()
                logger.info("FeatureExtractor singleton ready.")
    return _extractor


def get_ecg_predictor() -> ECGPredictor:
    """FastAPI Dependency: Lazy-load and return ECGPredictor singleton."""
    global _predictor
    if _predictor is None:
        with _lock:
            if _predictor is None:
                logger.info("Initializing ECGPredictor singleton...")
                _predictor = ECGPredictor()
                logger.info("ECGPredictor singleton ready.")
    return _predictor


# ========================================================
# HOME ENDPOINT
# ========================================================

@router.get(
    "/",
    response_model=HomeResponseModel,
    summary="Get Application Metadata",
    description="Returns root application branding, version, and running state."
)
def home() -> Dict[str, str]:
    """Home metadata endpoint."""
    return {
        "application": APP_NAME,
        "version": API_VERSION,
        "status": "Running"
    }


# ========================================================
# HEALTH CHECK ENDPOINT
# ========================================================

@router.get(
    "/health",
    response_model=HealthResponseModel,
    summary="System Health & Model Readiness",
    description="Check backend API operational health, ML model load state, and system uptime."
)
def health() -> Dict[str, Any]:
    """Health check endpoint."""
    uptime = round(time.time() - START_TIME, 2)
    model_ready = _predictor is not None and _extractor is not None
    return {
        "status": "healthy" if model_ready else "initializing",
        "model_loaded": model_ready,
        "uptime_seconds": uptime,
        "version": API_VERSION
    }


# ========================================================
# ECG PREDICTION ENDPOINT
# ========================================================

@router.post(
    "/predict",
    response_model=ECGPredictionResponseModel,
    summary="Classify 12-Lead ECG Record",
    description="Upload paired WFDB header (.hea) and signal data (.dat) files for classification and SHAP feature attribution."
)
async def predict(
    hea_file: UploadFile = File(..., description="WFDB header file (.hea)"),
    dat_file: UploadFile = File(..., description="WFDB binary signal file (.dat)"),
    extractor: FeatureExtractor = Depends(get_feature_extractor),
    predictor: ECGPredictor = Depends(get_ecg_predictor)
) -> Dict[str, Any]:
    """
    Upload a WFDB ECG record (.hea + .dat) and return clinical ECG classification payload.
    """
    t0 = time.perf_counter()
    logger.info(f"Received predict request: hea={hea_file.filename}, dat={dat_file.filename}")

    try:
        # 1. Process and parse uploaded WFDB record
        signal, metadata = ECGFileService.process_uploaded_record(hea_file, dat_file)

        # 2. Validate sampling rate and signal length
        sampling_rate = metadata.get("fs", 500)
        if sampling_rate != 500:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported sampling rate {sampling_rate} Hz. Only 500 Hz records are accepted."
            )

        if signal.shape[1] != 12:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 12-lead ECG recording, received {signal.shape[1]} leads."
            )

        if signal.shape[0] != 5000:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 10-second ECG recording (5000 samples at 500 Hz), received {signal.shape[0]} samples."
            )

        # 3. Assess 12-lead signal quality (SQI) and lead integrity
        lead_names = metadata.get("sig_name", [])
        signal_quality = ECGSignalValidator.calculate_sqi(signal, lead_names)
        clinical_warnings = ECGSignalValidator.generate_clinical_warnings(signal_quality, sampling_rate)

        # 4. Offload heavy feature extraction to worker threadpool
        extracted_features = await run_in_threadpool(extractor.extract_features, signal)
        t_extract = time.perf_counter() - t0

        # 5. Predict & Explain
        result = predictor.predict_ecg(
            extracted_features=extracted_features,
            signal_quality=signal_quality,
            base_warnings=clinical_warnings,
            record_info=metadata.get("record_info"),
            waveform_data=metadata.get("waveform_data")
        )

        total_duration = time.perf_counter() - t0
        logger.info(f"Record {hea_file.filename} processed in {total_duration:.3f}s (extraction: {t_extract:.3f}s)")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed for {hea_file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )