"""
=========================================================
Clinical Prediction Pipeline - v5 Model Architecture
ECG Clinical Decision Support System
=========================================================
Pipeline Responsibilities:
1. Align raw 322 extracted features with model schema
2. Apply v5 fitted preprocessor pipeline (Imputation, Clipping, Pruning, Scaling)
3. Execute XGBoost multi-label inference & threshold decision logic
4. Compute SHAP feature attributions on preprocessed features
5. Generate clinical risk tier, review guidance, and warnings
6. Return standardized JSON response matching API schema
=========================================================
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from backend.config.logging_config import setup_logger
from backend.config.settings import (
    CLINICAL_RECOMMENDATIONS,
    DEFAULT_RECOMMENDATION,
    MEDICAL_DISCLAIMER,
)
from backend.model_loader import ModelLoader
from backend.shap_explainer import SHAPExplainer

logger = setup_logger("predict_pipeline")


class ECGPredictor:
    """
    End-to-end ECG prediction and explainability engine for v5 model bundle.
    """

    def __init__(self) -> None:
        logger.info("Initializing ECGPredictor pipeline with v5 bundle loader...")
        self.loader = ModelLoader()
        self.explainer = SHAPExplainer(self.loader)
        logger.info("ECGPredictor Pipeline ready.")

    def align_raw_features(self, extracted_features: Dict[str, Any]) -> pd.DataFrame:
        """
        Align extracted features with the 322 raw feature names order.
        Missing features populated with np.nan.
        """
        feature_names = self.loader.feature_names_in
        arr = np.empty((1, len(feature_names)), dtype=np.float64)
        for i, feature in enumerate(feature_names):
            arr[0, i] = extracted_features.get(feature, np.nan)
        return pd.DataFrame(arr, columns=feature_names)

    def preprocess_features(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply v5 fitted pipeline (MissingFilter -> Imputer -> Clipper -> Pruner -> Scaler).
        Returns preprocessed DataFrame with 274 features.
        """
        clean_df = raw_df.replace([np.inf, -np.inf], np.nan)
        preprocessed_array = self.loader.preprocessor.transform(clean_df)
        return pd.DataFrame(preprocessed_array, columns=self.loader.feature_names_model)

    def predict_probabilities(self, preprocessed_df: pd.DataFrame) -> Dict[str, float]:
        """
        Execute predict_proba on preprocessed vector.
        Returns dict of class name -> probability percentage (0-100%).
        """
        raw_probas = self.loader.model.predict_proba(preprocessed_df)[0]
        prob_dict: Dict[str, float] = {}
        for i, class_name in enumerate(self.loader.class_names):
            prob = float(raw_probas[i])
            prob_dict[class_name] = round(prob * 100.0, 2)
        return prob_dict

    def evaluate_thresholds(self, prob_dict: Dict[str, float]) -> Tuple[List[str], str, float]:
        """
        Apply precision_target thresholds per class:
        predicted = prob >= threshold
        Returns (predicted_classes, primary_class, primary_confidence)
        """
        predicted_classes: List[str] = []
        for class_name in self.loader.class_names:
            prob_ratio = prob_dict[class_name] / 100.0
            thresh = self.loader.thresholds.get(class_name, 0.5)
            if prob_ratio >= thresh:
                predicted_classes.append(class_name)

        # Primary class selection logic:
        if predicted_classes:
            # Pick predicted class with highest margin above its threshold
            margins = {c: (prob_dict[c] / 100.0) - self.loader.thresholds.get(c, 0.5) for c in predicted_classes}
            primary_class = max(margins, key=margins.get)
        else:
            # Fallback if no class exceeds threshold: pick highest raw probability class
            primary_class = max(prob_dict, key=prob_dict.get)

        confidence = prob_dict[primary_class]
        return predicted_classes, primary_class, confidence

    @staticmethod
    def _calculate_clinical_risk(predicted_class: str, confidence: float) -> str:
        """Condition-aware clinical risk stratification logic."""
        if predicted_class == "MI":
            return "High"

        if predicted_class in ["STTC", "CD"]:
            if confidence >= 75.0:
                return "High"
            elif confidence >= 50.0:
                return "Medium"
            return "Low"

        if predicted_class == "HYP":
            if confidence >= 85.0:
                return "High"
            elif confidence >= 60.0:
                return "Medium"
            return "Low"

        if confidence >= 80.0:
            return "Low"
        return "Medium"

    @staticmethod
    def _get_recommendation(predicted_class: str) -> str:
        """Retrieve standardized medical recommendation for predicted class."""
        return CLINICAL_RECOMMENDATIONS.get(predicted_class, DEFAULT_RECOMMENDATION)

    def _generate_clinical_evidence(
        self,
        primary_class: str,
        confidence: float,
        predicted_classes: List[str],
        top_features: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate clinical evidence statements."""
        evidence: List[str] = [
            f"Model predicted primary diagnostic class {primary_class} with {confidence}% probability.",
        ]
        if len(predicted_classes) > 1:
            other = [c for c in predicted_classes if c != primary_class]
            evidence.append(f"Additional active threshold findings detected: {', '.join(other)}.")
        elif not predicted_classes:
            evidence.append("No diagnostic class exceeded its precision-target threshold.")

        if top_features:
            primary_feat = top_features[0]
            evidence.append(
                f"Primary feature contribution: {primary_feat.get('clean_name', primary_feat.get('Feature'))} "
                f"(SHAP score: {primary_feat.get('SHAP', 0):+.4f})."
            )
            if len(top_features) > 1:
                secondary_feat = top_features[1]
                evidence.append(
                    f"Secondary feature contribution: {secondary_feat.get('clean_name', secondary_feat.get('Feature'))} "
                    f"(SHAP score: {secondary_feat.get('SHAP', 0):+.4f})."
                )
        return evidence

    def _generate_review_guidance(self, predicted_class: str, risk_level: str) -> List[str]:
        """Generate non-autonomous clinician review guidance."""
        guidance_map: Dict[str, List[str]] = {
            "MI": [
                "Urgent cardiology consultation may be considered based on the clinical context.",
                "Inspect precordial and limb leads for ST elevation/depression or Q waves.",
                "Correlate with cardiac troponin I/T levels and clinical presentation (chest pain, dyspnea).",
                "Compare with prior baseline ECG tracings if available."
            ],
            "STTC": [
                "Examine 12-lead ECG for localized ST-segment deviation or T-wave inversions.",
                "Evaluate for potential myocardial ischemia, pericarditis, or electrolyte imbalance.",
                "Obtain serial ECG tracings and correlate with patient symptoms."
            ],
            "CD": [
                "Review PR interval, QRS duration, and QT/QTc interval metrics across all 12 leads.",
                "Inspect rhythm strip for heart block, bundle branch block, or axis deviation.",
                "Assess patient medication history for conduction-slowing agents."
            ],
            "HYP": [
                "Evaluate voltage criteria for left/right ventricular hypertrophy (S-V1 + R-V5/V6).",
                "Correlate with patient blood pressure trends and cardiovascular history.",
                "Consider confirmatory transthoracic echocardiography."
            ],
            "NORM": [
                "12-Lead ECG parameters fall within normal physiological reference ranges.",
                "Routine clinical follow-up may be considered based on the clinical context."
            ]
        }
        return guidance_map.get(predicted_class, [
            "Review 12-lead ECG signal morphology and correlate with patient clinical status."
        ])

    def predict_ecg(
        self,
        extracted_features: Dict[str, Any],
        signal_quality: Dict[str, Any] | None = None,
        base_warnings: List[str] | None = None,
        record_info: Dict[str, Any] | None = None,
        waveform_data: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Complete ECG prediction pipeline for v5 bundle.
        """
        logger.info("Executing v5 ECG prediction pipeline...")

        # 1. Align & Preprocess Features
        raw_df = self.align_raw_features(extracted_features)
        preprocessed_df = self.preprocess_features(raw_df)

        # 2. Compute Probabilities & Apply Precision-Target Thresholds
        prob_dict = self.predict_probabilities(preprocessed_df)
        predicted_classes, primary_class, confidence = self.evaluate_thresholds(prob_dict)

        risk_level = self._calculate_clinical_risk(primary_class, confidence)
        recommendation = self._get_recommendation(primary_class)

        # 3. Compute SHAP attributions for primary class
        top_features = self.explainer.top_features(preprocessed_df, primary_class)

        # 4. Evidence & Guidance
        clinical_evidence = self._generate_clinical_evidence(primary_class, confidence, predicted_classes, top_features)
        review_guidance = self._generate_review_guidance(primary_class, risk_level)

        # 5. Clinical Alerts & Warnings
        clinical_warnings: List[str] = list(base_warnings or [])
        if primary_class == "MI":
            clinical_warnings.insert(
                0,
                "CRITICAL ALERT: ECG pattern suggests acute Myocardial Infarction (MI). Immediate clinical evaluation required."
            )
        elif primary_class in ["CD", "STTC"] and risk_level == "High":
            clinical_warnings.insert(
                0,
                f"HIGH RISK ALERT: High probability of {primary_class} abnormality detected. Cardiology review advised."
            )

        logger.info(
            f"Prediction completed: primary={primary_class}, confidence={confidence}%, "
            f"predicted_active={predicted_classes}, risk={risk_level}"
        )

        response: Dict[str, Any] = {
            "diagnosis": primary_class,
            "confidence": confidence,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "probabilities": prob_dict,
            "top_features": top_features,
            "clinical_evidence": clinical_evidence,
            "review_guidance": review_guidance,
            "disclaimer": MEDICAL_DISCLAIMER,
        }

        if record_info:
            record_info["extracted_features_count"] = len(self.loader.feature_names_in)
            record_info["model_features_count"] = len(self.loader.feature_names_model)
            response["record_info"] = record_info

        if waveform_data:
            response["waveform_data"] = waveform_data
        if signal_quality:
            response["signal_quality"] = signal_quality
        if clinical_warnings:
            response["clinical_warnings"] = clinical_warnings

        return response