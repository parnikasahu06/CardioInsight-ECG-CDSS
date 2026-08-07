"""
=========================================================
Clinical Prediction Pipeline
ECG Clinical Decision Support System
=========================================================
Pipeline Responsibilities:
1. Align raw extracted features with model schema
2. Apply trained median imputer & standard scaler
3. Execute XGBoost multi-output prediction
4. Format class probabilities & calibrated confidence score
5. Apply condition-aware clinical risk stratification
6. Compute SHAP feature attributions
7. Return standardized clinical response payload with disclaimers
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
    End-to-end ECG prediction and clinical explainability engine.
    """

    def __init__(self) -> None:
        logger.info("Initializing ECGPredictor pipeline...")
        self.loader = ModelLoader()
        self.explainer = SHAPExplainer(self.loader)
        logger.info("ECGPredictor Pipeline ready.")

    def align_features(self, extracted_features: Dict[str, Any]) -> pd.DataFrame:
        """
        Align extracted features with trained model feature names order.
        Missing features are populated with np.nan for median imputation.
        Optimized with pre-allocated numpy array.
        """
        feature_names = self.loader.feature_names
        arr = np.empty((1, len(feature_names)), dtype=np.float64)
        for i, feature in enumerate(feature_names):
            arr[0, i] = extracted_features.get(feature, np.nan)
        return pd.DataFrame(arr, columns=feature_names)

    def apply_imputer(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill infinite or missing values using the trained median imputer.
        """
        clean_df = feature_df.replace([np.inf, -np.inf], np.nan)
        imputed_array = self.loader.imputer.transform(clean_df)
        return pd.DataFrame(imputed_array, columns=self.loader.feature_names)

    def apply_scaler(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Scale features using the trained StandardScaler.
        """
        scaled_array = self.loader.scaler.transform(feature_df)
        return pd.DataFrame(scaled_array, columns=self.loader.feature_names)

    def predict(self, scaled_df: pd.DataFrame) -> np.ndarray:
        """
        Execute raw multi-output classification.
        """
        return self.loader.model.predict(scaled_df)

    def predict_proba(self, scaled_df: pd.DataFrame) -> Any:
        """
        Predict class probabilities for each binary estimator.
        """
        return self.loader.model.predict_proba(scaled_df)

    def _preprocess_features(self, extracted_features: Dict[str, Any]) -> pd.DataFrame:
        """
        Internal pipeline helper: align, impute, and scale features.
        """
        aligned = self.align_features(extracted_features)
        imputed = self.apply_imputer(aligned)
        return self.apply_scaler(imputed)

    def _process_probabilities(
        self,
        prediction_vector: List[int],
        probabilities: Any
    ) -> Tuple[Dict[str, float], List[str], Dict[str, float]]:
        """
        Format raw estimator probabilities into percentage scores and confidence mappings.
        Only diagnostic classes trained in the model are evaluated.
        """
        probability_dict: Dict[str, float] = {}
        predicted_classes: List[str] = []
        confidence_scores: Dict[str, float] = {}

        for i, class_name in enumerate(self.loader.class_names):
            probability = float(probabilities[i][0][1])
            probability_dict[class_name] = round(probability * 100.0, 2)

            if prediction_vector[i] == 1:
                predicted_classes.append(class_name)
                confidence_scores[class_name] = probability

        return probability_dict, predicted_classes, confidence_scores

    @staticmethod
    def _calculate_clinical_risk(predicted_class: str, confidence: float) -> str:
        """
        Condition-aware clinical risk stratification logic:
        - MI (Myocardial Infarction) is automatically High Risk regardless of score.
        - STTC / CD are High Risk if confidence >= 75%, Medium if >= 50%.
        - HYP is High Risk if confidence >= 85%, Medium if >= 60%.
        - NORM is Low Risk if confidence >= 80%, Medium if < 80%.
        """
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

        # Default for NORM or other
        if confidence >= 80.0:
            return "Low"
        return "Medium"

    @staticmethod
    def _get_recommendation(predicted_class: str) -> str:
        """
        Retrieve standardized medical recommendation for predicted class.
        """
        return CLINICAL_RECOMMENDATIONS.get(predicted_class, DEFAULT_RECOMMENDATION)

    def _generate_clinical_evidence(
        self,
        predicted_class: str,
        confidence: float,
        top_features: List[Dict[str, Any]],
        probabilities: Dict[str, float]
    ) -> List[str]:
        """Generate evidence statements strictly from model probabilities and top SHAP attributions."""
        evidence: List[str] = [
            f"Model predicted primary diagnostic class {predicted_class} with {confidence}% probability.",
        ]
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
        Complete ECG prediction pipeline with clinical risk stratification and warnings.
        """
        logger.info("Executing ECG prediction pipeline...")

        scaled_df = self._preprocess_features(extracted_features)

        raw_prediction = self.predict(scaled_df)
        raw_probabilities = self.predict_proba(scaled_df)

        prediction_vector = raw_prediction[0].tolist()
        prob_dict, predicted_classes, confidence_scores = self._process_probabilities(
            prediction_vector, raw_probabilities
        )

        if not predicted_classes:
            logger.warning("No ECG class predicted by multi-output model.")
            return {"error": "No ECG class predicted."}

        predicted_class = predicted_classes[0]
        confidence = round(confidence_scores[predicted_class] * 100.0, 2)
        risk_level = self._calculate_clinical_risk(predicted_class, confidence)
        recommendation = self._get_recommendation(predicted_class)

        top_features = self.explainer.top_features(scaled_df, predicted_class)
        clinical_evidence = self._generate_clinical_evidence(predicted_class, confidence, top_features, prob_dict)
        review_guidance = self._generate_review_guidance(predicted_class, risk_level)

        # Assemble clinical warnings
        clinical_warnings: List[str] = list(base_warnings or [])
        if predicted_class == "MI":
            clinical_warnings.insert(
                0,
                "CRITICAL ALERT: ECG pattern suggests acute Myocardial Infarction (MI). Immediate clinical evaluation required."
            )
        elif predicted_class in ["CD", "STTC"] and risk_level == "High":
            clinical_warnings.insert(
                0,
                f"HIGH RISK ALERT: High probability of {predicted_class} abnormality detected. Cardiology review advised."
            )

        logger.info(
            f"Prediction completed: class={predicted_class}, confidence={confidence}%, risk={risk_level}"
        )

        response: Dict[str, Any] = {
            "diagnosis": predicted_class,
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
            response["record_info"] = record_info

        if waveform_data:
            response["waveform_data"] = waveform_data

        if signal_quality:
            response["signal_quality"] = signal_quality

        if clinical_warnings:
            response["clinical_warnings"] = clinical_warnings

        return response