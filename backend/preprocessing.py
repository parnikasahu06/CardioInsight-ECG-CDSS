"""
=========================================================
ECG Preprocessing Module
ECG Clinical Decision Support System
=========================================================
Responsibilities:
1. Read uploaded WFDB ECG records
2. Validate 12-lead signal dimensions and integrity
3. Return signal matrix and header metadata
=========================================================
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import numpy as np
import wfdb

from backend.config.logging_config import setup_logger

logger = setup_logger("preprocessing")


class ECGPreprocessor:
    """
    Reads and validates uploaded WFDB ECG records.
    """

    def load_record(
        self,
        record_path: Union[str, Path]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Load an ECG record using WFDB.

        Parameters
        ----------
        record_path : Union[str, Path]
            Base path to WFDB record file pair (without extension).

        Returns
        -------
        Tuple[np.ndarray, Dict[str, Any]]
            Tuple of (signal_array, metadata_dict).
        """
        str_path = str(record_path)
        try:
            signal, metadata = wfdb.rdsamp(str_path)
            return signal, metadata
        except Exception as e:
            logger.error(f"Failed to read WFDB record from {str_path}: {e}")
            raise RuntimeError(f"Unable to read ECG record at {str_path}: {e}") from e

    @staticmethod
    def validate_signal(
        signal: Union[np.ndarray, None],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Validate ECG signal matrix dimensions.
        """
        if signal is None or len(signal) == 0:
            raise ValueError("ECG signal is empty or contains no samples.")

        if signal.ndim != 2 or signal.shape[1] != 12:
            n_leads = signal.shape[1] if signal.ndim == 2 else "invalid"
            raise ValueError(f"Expected 12-lead ECG signal, found {n_leads} leads.")

        return True

    def process(self, record_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Execute full preprocessing and validation pipeline.
        """
        signal, metadata = self.load_record(record_path)
        self.validate_signal(signal, metadata)

        return {
            "signal": signal,
            "sampling_rate": metadata.get("fs", 500),
            "lead_names": metadata.get("sig_name", []),
            "samples": signal.shape[0],
            "n_leads": signal.shape[1],
        }