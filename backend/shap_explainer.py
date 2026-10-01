"""
=========================================================
Enhanced SHAP Explainability Module - v5 Pipeline
ECG Clinical Decision Support System
=========================================================
Generates SHAP feature attribution for XGBoost MultiLabel model.
Computes SHAP on the 274 preprocessed features and returns clean
attributions formatted for frontend visualization.
=========================================================
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
import shap

from backend.config.logging_config import setup_logger
from backend.config.settings import MEDICAL_TERMINOLOGY
from backend.model_loader import ModelLoader

logger = setup_logger("shap_explainer")


class SHAPExplainer:
    """
    Computes feature attributions using pre-warmed SHAP TreeExplainers
    for each binary class estimator in XGBMultiLabel.
    """

    def __init__(self, loader: ModelLoader) -> None:
        self.loader = loader
        self.model = loader.model
        self.feature_names = loader.feature_names_model
        self.class_labels = list(loader.class_names)

        logger.info("Initializing pre-warmed SHAP TreeExplainers for v5 estimators...")
        self.explainers: List[shap.TreeExplainer] = [
            shap.TreeExplainer(estimator) for estimator in self.model.estimators_
        ]
        logger.info(f"Initialized {len(self.explainers)} SHAP TreeExplainers for classes {self.class_labels}.")

    @staticmethod
    def _format_clean_name(feature_raw: str) -> str:
        """Format raw feature identifier into physician-readable text."""
        tokens = feature_raw.split("_")
        lead_prefix = tokens[0].upper()

        if lead_prefix in ["I", "II", "III", "AVR", "AVL", "AVF", "V1", "V2", "V3", "V4", "V5", "V6"]:
            stat = " ".join(tokens[1:]).capitalize()
            return f"Lead {lead_prefix} {stat}".strip()

        return feature_raw.replace("_", " ").title()

    @classmethod
    def _generate_interpretation(cls, clean_name: str, shap_value: float, class_name: str) -> str:
        """Generate clinical interpretation sentence for a SHAP attribution."""
        term_info = MEDICAL_TERMINOLOGY.get(class_name, {})
        full_condition = term_info.get("full_name", class_name)
        sign_str = f"+{shap_value:.4f}" if shap_value >= 0 else f"{shap_value:.4f}"

        if shap_value >= 0:
            return f"{clean_name} ({sign_str}) strongly supports the diagnosis of {full_condition} ({class_name})."
        else:
            return (
                f"{clean_name} ({sign_str}) acts as a suppressing factor, reducing "
                f"the likelihood of {full_condition} ({class_name})."
            )

    def top_features(self, preprocessed_df: pd.DataFrame, target_class: str) -> List[Dict[str, Any]]:
        """
        Compute top 5 SHAP feature importances for the specified target class.
        preprocessed_df: DataFrame with shape (1, 274) matching feature_names_model.
        """
        if target_class not in self.class_labels:
            logger.warning(f"Target class {target_class} not found in model class labels {self.class_labels}.")
            target_class = self.class_labels[0]

        class_idx = self.class_labels.index(target_class)
        explainer = self.explainers[class_idx]

        shap_values = explainer.shap_values(preprocessed_df)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        values = shap_values[0]
        abs_values = np.abs(values)
        top_indices = np.argsort(abs_values)[::-1][:5]

        feature_records: List[Dict[str, Any]] = []
        for idx in top_indices:
            feat_raw = self.feature_names[idx]
            val_shap = float(values[idx])
            val_abs_shap = float(abs_values[idx])
            clean_name = self._format_clean_name(feat_raw)
            direction = "positive" if val_shap >= 0 else "negative"
            interpretation = self._generate_interpretation(clean_name, val_shap, target_class)

            feature_records.append({
                "Feature": feat_raw,
                "SHAP": round(val_shap, 6),
                "AbsSHAP": round(val_abs_shap, 6),
                "clean_name": clean_name,
                "direction": direction,
                "interpretation": interpretation,
            })

        return feature_records