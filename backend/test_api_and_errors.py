"""
=========================================================
v5 Verification Suite: Tests D, E, F (API & Error Handling)
=========================================================
Tests:
- Test D: End-to-End API Prediction Flow with real WFDB files
- Test E: Error Handling & Edge Case Validation (HTTP 400 & zero backend crash)
- Test F: API Response JSON Schema & Contract Integrity
=========================================================
"""

import io
import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.schemas.ecg_schemas import ECGPredictionResponseModel

client = TestClient(app)

DATA_DIR = os.environ.get("DATA_DIR", "data/ptb-xl")
RECORD_DIR = os.path.join(DATA_DIR, "records500/00000")
RECORD_BASE = os.path.join(RECORD_DIR, "00001_hr")


class TestV5APIAndErrors(unittest.TestCase):

    def test_d_end_to_end_prediction(self):
        """Test D: Valid 500 Hz 12-lead record upload return HTTP 200 and full valid payload."""
        hea_file_path = f"{RECORD_BASE}.hea"
        dat_file_path = f"{RECORD_BASE}.dat"

        if not os.path.exists(hea_file_path) or not os.path.exists(dat_file_path):
            print(f"\n[SKIP] PTB-XL sample record not found at '{hea_file_path}'. Set DATA_DIR environment variable to run end-to-end API upload test.")
            self.skipTest(f"Record file missing at {hea_file_path}")

        with open(hea_file_path, "rb") as f_hea, open(dat_file_path, "rb") as f_dat:
            files = {
                "hea_file": ("00001_hr.hea", f_hea.read(), "text/plain"),
                "dat_file": ("00001_hr.dat", f_dat.read(), "application/octet-stream")
            }

        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}: {response.text}")

        data = response.json()
        print("\n--- Test D: End-to-End Prediction Payload ---")
        print("Diagnosis:", data.get("diagnosis"))
        print("Confidence:", data.get("confidence"))
        print("Probabilities:", data.get("probabilities"))
        print("Top Features count:", len(data.get("top_features", [])))

        # Verify required keys in response
        required_keys = [
            "diagnosis", "confidence", "risk_level", "recommendation",
            "probabilities", "top_features", "clinical_evidence",
            "review_guidance", "disclaimer", "record_info",
            "waveform_data", "signal_quality"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Missing key '{key}' in prediction response")

        # Verify diagnostic classes in probabilities dict
        expected_classes = {"CD", "HYP", "MI", "NORM", "STTC"}
        self.assertEqual(set(data["probabilities"].keys()), expected_classes)

        # Validate Pydantic schema
        model_instance = ECGPredictionResponseModel(**data)
        self.assertIsNotNone(model_instance)
        print("Test D passed successfully!")

    def test_e1_mismatched_filenames(self):
        """Test E1: Mismatched .hea and .dat file stems return HTTP 400."""
        files = {
            "hea_file": ("00001_hr.hea", b"header_content", "text/plain"),
            "dat_file": ("00002_hr.dat", b"signal_content", "application/octet-stream")
        }
        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Mismatched WFDB record pair", response.json()["detail"])
        print("Test E1 (Mismatched Pair) passed!")

    def test_e2_invalid_extensions(self):
        """Test E2: Non .hea or non .dat file extensions return HTTP 400."""
        files = {
            "hea_file": ("00001_hr.txt", b"header_content", "text/plain"),
            "dat_file": ("00001_hr.dat", b"signal_content", "application/octet-stream")
        }
        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("must have a .hea extension", response.json()["detail"])
        print("Test E2 (Invalid Extension) passed!")

    def test_e3_empty_file(self):
        """Test E3: Empty (0-byte) file returns HTTP 400."""
        files = {
            "hea_file": ("00001_hr.hea", b"", "text/plain"),
            "dat_file": ("00001_hr.dat", b"some content", "application/octet-stream")
        }
        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("is empty", response.json()["detail"])
        print("Test E3 (Empty File) passed!")

    def test_e4_corrupt_wfdb_file(self):
        """Test E4: Corrupt WFDB content returns HTTP 400 without crashing backend."""
        files = {
            "hea_file": ("00001_hr.hea", b"corrupted header content non-wfdb format", "text/plain"),
            "dat_file": ("00001_hr.dat", b"corrupted binary content", "application/octet-stream")
        }
        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Invalid WFDB format" in response.json()["detail"] or "WFDB Record Error" in response.json()["detail"])
        print("Test E4 (Corrupt WFDB) passed!")

    def test_e5_100hz_sampling_rate(self):
        """Test E5: Record sampled at 100 Hz returns HTTP 400."""
        hea_content = b"00001_lr 12 100 1000\n00001_lr.dat 16 1000/mV 16 0 0 0 0 I\n00001_lr.dat 16 1000/mV 16 0 0 0 0 II\n00001_lr.dat 16 1000/mV 16 0 0 0 0 III\n00001_lr.dat 16 1000/mV 16 0 0 0 0 aVR\n00001_lr.dat 16 1000/mV 16 0 0 0 0 aVL\n00001_lr.dat 16 1000/mV 16 0 0 0 0 aVF\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V1\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V2\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V3\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V4\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V5\n00001_lr.dat 16 1000/mV 16 0 0 0 0 V6\n"
        dat_content = b"\x00" * 24000  # 1000 samples * 12 leads * 2 bytes
        files = {
            "hea_file": ("00001_lr.hea", hea_content, "text/plain"),
            "dat_file": ("00001_lr.dat", dat_content, "application/octet-stream")
        }
        response = client.post("/predict", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported sampling rate", response.json()["detail"])
        print("Test E5 (100 Hz Sampling Rate) passed!")

    def test_f_api_contract_diff(self):
        """Test F: Ensure JSON output matches exact schema types and range boundaries."""
        hea_file_path = f"{RECORD_BASE}.hea"
        dat_file_path = f"{RECORD_BASE}.dat"

        if not os.path.exists(hea_file_path) or not os.path.exists(dat_file_path):
            print(f"\n[SKIP] PTB-XL sample record not found at '{hea_file_path}'. Set DATA_DIR environment variable to run API contract test.")
            self.skipTest(f"Record file missing at {hea_file_path}")

        with open(hea_file_path, "rb") as f_hea, open(dat_file_path, "rb") as f_dat:
            files = {
                "hea_file": ("00001_hr.hea", f_hea.read(), "text/plain"),
                "dat_file": ("00001_hr.dat", f_dat.read(), "application/octet-stream")
            }

        response = client.post("/predict", files=files)
        data = response.json()

        # Contract checks
        self.assertIsInstance(data["diagnosis"], str)
        self.assertIsInstance(data["confidence"], float)
        self.assertTrue(0.0 <= data["confidence"] <= 100.0)
        self.assertIn(data["risk_level"], ["Low", "Medium", "High"])
        self.assertIsInstance(data["recommendation"], str)

        for k, v in data["probabilities"].items():
            self.assertIsInstance(v, float)
            self.assertTrue(0.0 <= v <= 100.0)

        for feat in data["top_features"]:
            self.assertIn("Feature", feat)
            self.assertIn("SHAP", feat)
            self.assertIn("AbsSHAP", feat)
            self.assertIn("clean_name", feat)
            self.assertIn("direction", feat)
            self.assertIn("interpretation", feat)

        print("Test F (API Contract Diff) passed successfully!")


if __name__ == "__main__":
    unittest.main()
