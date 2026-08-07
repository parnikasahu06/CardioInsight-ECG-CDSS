import datetime
import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Any, Dict, Generator, Tuple
import numpy as np
import wfdb
from fastapi import UploadFile, HTTPException

from backend.config.logging_config import setup_logger

logger = setup_logger("ecg_service")


class ECGFileService:
    """
    Service layer for managing WFDB file uploads, record reading,
    detailed error validation, and waveform serialization.
    """

    @staticmethod
    def validate_file_extensions(hea_filename: str, dat_filename: str) -> None:
        """
        Validate uploaded file extensions and names.
        """
        if not hea_filename:
            raise HTTPException(
                status_code=400,
                detail="Missing header file (.hea). Please select both .hea and .dat files."
            )
        if not dat_filename:
            raise HTTPException(
                status_code=400,
                detail="Missing binary signal data file (.dat). Please select both .hea and .dat files."
            )

        if not hea_filename.lower().endswith(".hea"):
            logger.warning(f"Invalid header file extension: {hea_filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{hea_filename}'. Header file must have a .hea extension."
            )

        if not dat_filename.lower().endswith(".dat"):
            logger.warning(f"Invalid signal file extension: {dat_filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{dat_filename}'. Signal data file must have a .dat extension."
            )

        hea_stem = os.path.splitext(hea_filename)[0]
        dat_stem = os.path.splitext(dat_filename)[0]

        if hea_stem != dat_stem:
            logger.warning(f"Mismatched WFDB record pair: {hea_filename} vs {dat_filename}")
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Mismatched WFDB record pair: Uploaded header '{hea_filename}' does not match "
                    f"signal file '{dat_filename}'. Header base name ('{hea_stem}') and signal base name "
                    f"('{dat_stem}') must match."
                )
            )

    @staticmethod
    @contextmanager
    def create_temp_dir() -> Generator[str, None, None]:
        """
        Context manager to create a temporary directory and guarantee cleanup.
        """
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    @classmethod
    def process_uploaded_record(
        cls,
        hea_file: UploadFile,
        dat_file: UploadFile
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Save uploaded WFDB files to a temp directory, parse using WFDB,
        and return the raw 12-lead signal array along with rich metadata dict.
        """
        cls.validate_file_extensions(hea_file.filename or "", dat_file.filename or "")

        with cls.create_temp_dir() as temp_dir:
            hea_filename = hea_file.filename or "record.hea"
            dat_filename = dat_file.filename or "record.dat"
            hea_path = os.path.join(temp_dir, hea_filename)
            dat_path = os.path.join(temp_dir, dat_filename)

            try:
                hea_file.file.seek(0)
                dat_file.file.seek(0)
                hea_content = hea_file.file.read()
                dat_content = dat_file.file.read()

                if len(hea_content) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Header file '{hea_filename}' is empty (0 bytes)."
                    )
                if len(dat_content) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Signal data file '{dat_filename}' is empty (0 bytes)."
                    )

                with open(hea_path, "wb") as f:
                    f.write(hea_content)
                with open(dat_path, "wb") as f:
                    f.write(dat_content)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to write uploaded files to temporary storage: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Corrupted or invalid file upload stream: {str(e)}"
                )

            record_name = os.path.splitext(hea_filename)[0]
            record_base_path = os.path.join(temp_dir, record_name)

            logger.info(f"Reading WFDB record: {record_name}")
            try:
                record = wfdb.rdrecord(record_base_path)
            except Exception as e:
                logger.error(f"WFDB reader error for {record_name}: {e}")
                err_msg = str(e)
                if "No such file" in err_msg or "Cannot open" in err_msg:
                    detail_str = (
                        f"WFDB Record Error: Header '{hea_filename}' references a missing or incorrectly named "
                        f"binary file. Ensure '{dat_filename}' matches the signal file defined in the header."
                    )
                else:
                    detail_str = f"Invalid WFDB format in '{hea_filename}': {err_msg}"
                raise HTTPException(
                    status_code=400,
                    detail=detail_str
                )

            if record is None or record.p_signal is None or len(record.p_signal) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="WFDB signal data is empty, corrupted, or unreadable."
                )

            signal = record.p_signal
            fs = float(getattr(record, "fs", 500))
            sig_name = getattr(record, "sig_name", None)
            if not sig_name or len(sig_name) != signal.shape[1]:
                standard_leads = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
                sig_name = standard_leads[: signal.shape[1]]

            n_samples, n_leads = signal.shape
            duration_seconds = round(n_samples / fs, 2)

            # Downsample for web chart visualization (max 1000 points per lead for smooth SVG/Canvas rendering)
            max_points = 1000
            step = max(1, n_samples // max_points)
            sampled_indices = np.arange(0, n_samples, step)
            sampled_signal = signal[sampled_indices, :]
            sampled_time = np.round(sampled_indices / fs, 3).tolist()

            leads_dict: Dict[str, list] = {}
            for i, name in enumerate(sig_name):
                # Clean up NaN / Inf and round to 4 decimal places
                clean_lead = np.nan_to_num(sampled_signal[:, i], nan=0.0, posinf=0.0, neginf=0.0)
                leads_dict[name] = np.round(clean_lead, 4).tolist()

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            metadata: Dict[str, Any] = {
                "record_info": {
                    "record_id": record_name,
                    "timestamp": timestamp,
                    "fs": fs,
                    "duration_seconds": duration_seconds,
                    "n_leads": n_leads,
                    "hea_filename": hea_filename,
                    "dat_filename": dat_filename,
                },
                "waveform_data": {
                    "leads": leads_dict,
                    "time": sampled_time,
                    "fs": fs,
                },
                "fs": fs,
                "sig_name": sig_name,
                "comments": getattr(record, "comments", []),
            }

            return signal, metadata

