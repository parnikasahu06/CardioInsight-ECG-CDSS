"""
=========================================================
Enhanced & Optimized SHAP Explainability Module
ECG Clinical Decision Support System
=========================================================
Generates feature importance using SHAP for the trained
XGBoost MultiOutputClassifier.
Pre-caches TreeExplainer instances, performs targeted single-class
attributions for fast inference, and formats output for Recharts UI.
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
    Computes feature attribution using SHAP TreeExplainer for multi-output XGBoost models.
    Pre-caches explainers for each class estimator to optimize inference speed.
    """

    def __init__(self, loader: ModelLoader) -> None:
        self.loader = loader
        self.model = loader.model
        self.feature_names = loader.feature_names
        self.class_labels = list(loader.class_names)

        logger.info("Initializing pre-warmed SHAP TreeExplainers for each estimator...")
        self.explainers: List[shap.TreeExplainer] = [
            shap.TreeExplainer(estimator) for estimator in self.model.estimators_
        ]
        logger.info(f"Initialized {len(self.explainers)} SHAP TreeExplainers.")

    @staticmethod
    def _format_clean_name(feature_raw: str) -> str:
        """
        Format raw feature identifier into a physician-readable string.
        """
        tokens = feature_raw.split("_")
        lead_prefix = tokens[0].upper()

        if lead_prefix in ["I", "II", "III", "AVR", "AVL", "AVF", "V1", "V2", "V3", "V4", "V5", "V6"]:
            stat = " ".join(tokens[1:]).capitalize()
            return f"Lead {lead_prefix} {stat}".strip()

        return feature_raw.replace("_", " ").title()

    @classmethod
    def _generate_interpretation(
        cls,
        clean_name: str,
        shap_value: float,
        class_name: str
    ) -> str:
        """
        Generate contextual clinical interpretation sentence for a SHAP feature impact.
        """
        term_info = MEDICAL_TERMINOLOGY.get(class_name, {})
        full_condition = term_info.get("full_name", class_name)
        sign_str = f"+{shap_value:.4f}" if shap_value >= 0 else f"{shap_value:.4f}"

        if shap_value >= 0:
            return (
                f"{clean_name} ({sign_str}) strongly supports the diagnosis of "
                f"{full_condition} ({class_name})."
            )
        else:
            return (
                f"{clean_name} ({sign_str}) acts as a suppressing factor, reducing "
                f"the likelihood of {full_condition} ({class_name})."
            )

    def explain(self, scaled_features: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compute top 5 SHAP feature importances for all diagnostic classes.
        """
        explanations: Dict[str, List[Dict[str, Any]]] = {}

        for i, explainer in enumerate(self.explainers):
            class_name = self.class_labels[i]
            shap_values = explainer.shap_values(scaled_features)

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
                interpretation = self._generate_interpretation(clean_name, val_shap, class_name)

                feature_records.append({
                    "Feature": feat_raw,
                    "SHAP": round(val_shap, 6),
                    "AbsSHAP": round(val_abs_shap, 6),
                    "clean_name": clean_name,
                    "direction": direction,
                    "interpretation": interpretation,
                })

            explanations[class_name] = feature_records

        return explanations

    def top_features(
        self,
        scaled_features: pd.DataFrame,
        predicted_class: str
    ) -> List[Dict[str, Any]]:
        """
        Optimized single-class SHAP feature extraction:
        Computes SHAP values ONLY for the target predicted class estimator,
        cutting execution time significantly.
        """
        if predicted_class in self.class_labels:
            class_idx = self.class_labels.index(predicted_class)
            explainer = self.explainers[class_idx]

            shap_values = explainer.shap_values(scaled_features)
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
                interpretation = self._generate_interpretation(clean_name, val_shap, predicted_class)

                feature_records.append({
                    "Feature": feat_raw,
                    "SHAP": round(val_shap, 6),
                    "AbsSHAP": round(val_abs_shap, 6),
                    "clean_name": clean_name,
                    "direction": direction,
                    "interpretation": interpretation,
                })

            return feature_records

        explanation = self.explain(scaled_features)
        return explanation.get(predicted_class, [])