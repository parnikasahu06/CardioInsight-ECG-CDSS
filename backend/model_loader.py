"""
=========================================================
Model Loader
ECG Clinical Decision Support System
=========================================================
Loads trained machine learning artifacts:
    - XGBoost Multi-Output Model
    - Standard Scaler
    - Median Imputer
    - Feature Names list
    - Diagnostic Class Names
=========================================================
"""

from typing import Any, List
import joblib
import numpy as np
import pandas as pd

from backend.config.logging_config import setup_logger
from backend.config.settings import (
    MODEL_PATH,
    SCALER_PATH,
    IMPUTER_PATH,
    FEATURE_NAMES_PATH,
    CLASS_NAMES_PATH,
)

logger = setup_logger("model_loader")


class ModelLoader:
    """
    Singleton-style loader for trained ML artifacts.
    """

    def __init__(self) -> None:
        logger.info("Loading trained ML artifacts...")

        try:
            self.model: Any = joblib.load(MODEL_PATH)
            logger.info(f"Loaded XGBoost Model from {MODEL_PATH.name}")

            self.scaler: Any = joblib.load(SCALER_PATH)
            logger.info(f"Loaded StandardScaler from {SCALER_PATH.name}")

            self.imputer: Any = joblib.load(IMPUTER_PATH)
            logger.info(f"Loaded Median Imputer from {IMPUTER_PATH.name}")

            feature_df = pd.read_csv(FEATURE_NAMES_PATH)
            self.feature_names: List[str] = feature_df.iloc[:, 0].tolist()
            logger.info(f"Loaded {len(self.feature_names)} feature names")

            raw_classes = np.load(CLASS_NAMES_PATH, allow_pickle=True)
            self.class_names: List[str] = [str(cls) for cls in raw_classes]
            logger.info(f"Loaded {len(self.class_names)} diagnostic classes: {self.class_names}")

            logger.info("Model Loader initialization complete.")

        except FileNotFoundError as e:
            logger.error(f"Failed to load model artifact: {e}")
            raise FileNotFoundError(f"Missing required model artifact: {e.filename}") from e
        except Exception as e:
            logger.error(f"Unexpected error while loading artifacts: {e}")
            raise RuntimeError(f"Error loading ML artifacts: {e}") from e