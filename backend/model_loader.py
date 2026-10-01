"""
=========================================================
Model Loader - v5 Bundle Architecture
ECG Clinical Decision Support System
=========================================================
Loads trained v5 model bundle artifact:
    - Preprocessing Pipeline (MissingFilter, Imputer, Clipper, Pruner, Scaler)
    - XGBoost Multi-Output Model (XGBMultiLabel)
    - Precision-Target Class Thresholds
    - Raw & Model Feature Name Lists
    - Diagnostic Class Names
=========================================================
"""

import sys
import os
from typing import Any, Dict, List
import joblib
import numpy as np

from backend.config.logging_config import setup_logger
import backend.ecg_pipeline as ep

logger = setup_logger("model_loader")

# Inject classes into __main__ before joblib.load for pickle compatibility
main_dict = sys.modules["__main__"].__dict__
main_dict["MissingFilter"] = ep.MissingFilter
main_dict["QuantileClipper"] = ep.QuantileClipper
main_dict["CorrelationPruner"] = ep.CorrelationPruner
main_dict["XGBMultiLabel"] = ep.XGBMultiLabel
main_dict["XGBClassifierChain"] = ep.XGBClassifierChain


class ModelLoader:
    """
    Singleton loader for v5 trained ML bundle.
    """

    def __init__(self, bundle_path: str = "models/trained/v5_ecg_model_bundle.pkl") -> None:
        logger.info(f"Loading trained v5 ML model bundle from {bundle_path}...")

        # Fallback to outputs/v5_final if local models/trained file not yet generated
        if not os.path.exists(bundle_path):
            fallback = "outputs/v5_final/ecg_model_bundle.pkl"
            logger.info(f"Local path {bundle_path} not found. Falling back to {fallback}")
            bundle_path = fallback

        try:
            self.bundle: Dict[str, Any] = joblib.load(bundle_path)
            self.model: Any = self.bundle["model"]
            self.preprocessor: Any = self.bundle["preprocess"]
            self.class_names: List[str] = list(self.bundle["class_names"])
            raw_thresholds = self.bundle["thresholds"]
            if isinstance(raw_thresholds, (list, tuple, np.ndarray)):
                self.thresholds: Dict[str, float] = {
                    cls: round(float(thresh), 4) for cls, thresh in zip(self.class_names, raw_thresholds)
                }
            else:
                self.thresholds: Dict[str, float] = {k: round(float(v), 4) for k, v in raw_thresholds.items()}
            self.feature_names_in: List[str] = list(self.bundle["feature_names_in"])
            self.feature_names_model: List[str] = list(self.bundle["feature_names_model"])
            self.sampling_rate: int = int(self.bundle.get("sampling_rate", 500))

            # Maintain backward compatibility attribute references
            self.feature_names: List[str] = self.feature_names_model

            logger.info(
                f"Successfully loaded v5 model bundle ({len(self.feature_names_in)} raw features, "
                f"{len(self.feature_names_model)} model features, classes: {self.class_names})"
            )

        except FileNotFoundError as e:
            logger.error(f"Failed to load model artifact: {e}")
            raise FileNotFoundError(f"Missing required model bundle: {e.filename}") from e
        except Exception as e:
            logger.error(f"Unexpected error while loading bundle: {e}")
            raise RuntimeError(f"Error loading ML bundle: {e}") from e