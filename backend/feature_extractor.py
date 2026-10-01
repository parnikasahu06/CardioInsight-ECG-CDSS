"""
=========================================================
Feature Extractor - v5 Pipeline Wrapper
ECG Clinical Decision Support System
=========================================================
Wraps ecg_pipeline.py to provide a clean interface for extracting
all 322 raw ECG features from a 12-lead signal matrix (shape 5000x12, 500 Hz).
=========================================================
"""

from typing import Any, Dict
import numpy as np

from backend.config.logging_config import setup_logger
from backend.ecg_pipeline import SAMPLING_RATE, extract_complete_features

logger = setup_logger("feature_extractor")


class FeatureExtractor:
    """
    Extracts 322 raw features from a 12-lead ECG signal matrix.
    """

    def __init__(self, sampling_rate: int = SAMPLING_RATE) -> None:
        self.sampling_rate = sampling_rate

    def extract_features(self, signal: np.ndarray) -> Dict[str, Any]:
        """
        Extract complete 322 raw features from 12-lead ECG signal.
        """
        logger.info(f"Extracting complete v5 features from signal shape {signal.shape} at {self.sampling_rate} Hz...")
        features = extract_complete_features(signal, self.sampling_rate)
        logger.info(f"Extracted {len(features)} raw ECG features.")
        return features
