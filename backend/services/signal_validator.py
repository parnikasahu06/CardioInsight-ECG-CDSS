"""
=========================================================
Clinical ECG Signal Validator & Quality Assessor
ECG Clinical Decision Support System
=========================================================
Responsibilities:
1. Assess 12-lead ECG signal quality (SQI calculation)
2. Detect flatline / disconnected leads
3. Detect railing / saturation / extreme noise artifacts
4. Generate structured clinical warnings for attending medical staff
=========================================================
"""

from typing import Any, Dict, List, Tuple
import numpy as np

from backend.config.logging_config import setup_logger

logger = setup_logger("signal_validator")

STANDARD_LEAD_NAMES = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]


class ECGSignalValidator:
    """
    Evaluates 12-lead ECG signal integrity, calculates Signal Quality Index (SQI),
    and generates clinical risk warnings.
    """

    @staticmethod
    def assess_lead_integrity(
        signal: np.ndarray,
        lead_names: List[str] | None = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Identify flatline (disconnected), saturated, and noisy leads.

        Parameters
        ----------
        signal : np.ndarray
            ECG signal matrix (n_samples x n_leads).
        lead_names : List[str], optional
            Names of the 12 leads.

        Returns
        -------
        Tuple[List[str], List[str], List[str]]
            (flatline_leads, saturated_leads, noisy_leads)
        """
        names = lead_names if lead_names and len(lead_names) == signal.shape[1] else STANDARD_LEAD_NAMES

        flatline_leads: List[str] = []
        saturated_leads: List[str] = []
        noisy_leads: List[str] = []

        for col_idx in range(signal.shape[1]):
            lead_signal = signal[:, col_idx]
            lead_name = names[col_idx] if col_idx < len(names) else f"Lead_{col_idx + 1}"

            # Remove NaNs for stat computation
            valid_samples = lead_signal[~np.isnan(lead_signal)]
            if len(valid_samples) == 0:
                flatline_leads.append(lead_name)
                continue

            std_dev = float(np.std(valid_samples))
            amplitude_range = float(np.ptp(valid_samples))

            # Flatline check (std dev < 0.001 mV or zero range)
            if std_dev < 1e-4 or amplitude_range < 1e-3:
                flatline_leads.append(lead_name)

            # Saturation check (amplitude > 15.0 mV or max > 20.0 mV)
            elif np.max(np.abs(valid_samples)) > 15.0:
                saturated_leads.append(lead_name)

            # High variance / extreme noise check
            elif std_dev > 4.0:
                noisy_leads.append(lead_name)

        return flatline_leads, saturated_leads, noisy_leads

    @classmethod
    def calculate_sqi(
        cls,
        signal: np.ndarray,
        lead_names: List[str] | None = None
    ) -> Dict[str, Any]:
        """
        Calculate overall Signal Quality Index (SQI) percentage and status.

        Parameters
        ----------
        signal : np.ndarray
            Raw signal array.
        lead_names : List[str], optional
            Lead names list.

        Returns
        -------
        Dict[str, Any]
            Quality metrics dict containing sqi_score, status, and lead details.
        """
        n_samples, n_leads = signal.shape
        flatline, saturated, noisy = cls.assess_lead_integrity(signal, lead_names)

        invalid_lead_count = len(flatline) + len(saturated)
        valid_lead_ratio = max(0.0, (n_leads - invalid_lead_count) / float(n_leads))

        # Check NaN sample ratio across matrix
        nan_count = int(np.isnan(signal).sum())
        total_elements = signal.size
        nan_ratio = nan_count / float(total_elements) if total_elements > 0 else 0.0

        # Calculate base SQI score (0 - 100%)
        sqi_score = round((valid_lead_ratio * 0.7 + (1.0 - nan_ratio) * 0.3) * 100.0, 1)

        # Subtract penalty for noisy leads
        if noisy:
            sqi_score = max(0.0, sqi_score - (len(noisy) * 5.0))

        if sqi_score >= 85.0:
            status = "Excellent"
        elif sqi_score >= 65.0:
            status = "Acceptable"
        else:
            status = "Poor"

        return {
            "sqi_score": sqi_score,
            "status": status,
            "samples": n_samples,
            "n_leads": n_leads,
            "flatline_leads": flatline,
            "saturated_leads": saturated,
            "noisy_leads": noisy,
        }

    @classmethod
    def generate_clinical_warnings(
        cls,
        signal_quality: Dict[str, Any],
        sampling_rate: int = 500
    ) -> List[str]:
        """
        Generate human-readable clinical warnings based on signal quality assessment.
        """
        warnings: List[str] = []

        if sampling_rate != 500:
            warnings.append(
                f"Sampling rate mismatch: Received {sampling_rate} Hz. Model requires 500 Hz."
            )

        flatline = signal_quality.get("flatline_leads", [])
        if flatline:
            warnings.append(
                f"Flatline / Disconnected lead detected on: {', '.join(flatline)}. Verify lead attachment."
            )

        saturated = signal_quality.get("saturated_leads", [])
        if saturated:
            warnings.append(
                f"Voltage saturation artifact detected on: {', '.join(saturated)}."
            )

        noisy = signal_quality.get("noisy_leads", [])
        if noisy:
            warnings.append(
                f"High baseline noise / muscle artifact on: {', '.join(noisy)}."
            )

        sqi_score = signal_quality.get("sqi_score", 100.0)
        if sqi_score < 65.0:
            warnings.append(
                "Poor overall signal quality (SQI < 65%). Repeat ECG recording prior to definitive diagnosis."
            )

        return warnings
