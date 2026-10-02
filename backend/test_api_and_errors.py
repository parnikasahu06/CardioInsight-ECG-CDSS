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

        # Verify only allowed fields (legacy 13 + 4 optional) appear in payload
        allowed_keys = {
            "diagnosis", "confidence", "risk_level", "recommendation",
            "probabilities", "top_features", "clinical_evidence",
            "review_guidance", "disclaimer", "record_info",
            "waveform_data", "signal_quality", "clinical_warnings",
            "positive_classes", "decision_status", "top_class_below_threshold", "decision_thresholds"
        }
        for key in data.keys():
            self.assertIn(key, allowed_keys, f"Unexpected field '{key}' in API response payload")

        if "positive_classes" in data:
            self.assertIsInstance(data["positive_classes"], list)
        if "decision_status" in data:
            self.assertIn(data["decision_status"], ["positive", "no_class_above_threshold"])
        if "top_class_below_threshold" in data:
            self.assertIsInstance(data["top_class_below_threshold"], bool)
        if "decision_thresholds" in data:
            self.assertIsInstance(data["decision_thresholds"], dict)
            self.assertEqual(data["decision_thresholds"].get("NORM"), 0.88)

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

    def test_g_synthetic_evaluate_thresholds(self):
        """Test G: Synthetic unit test of evaluate_thresholds covering multi-positive, all-below, and exact-threshold cases."""
        from backend.predict import evaluate_thresholds

        # Case 1: Two classes positive (CD 80%, HYP 50%). Headline must be CD (higher probability).
        probs_two_pos = {"CD": 80.0, "HYP": 50.0, "MI": 10.0, "NORM": 10.0, "STTC": 10.0}
        res_two_pos = evaluate_thresholds(probs_two_pos)
        self.assertEqual(res_two_pos["primary_class"], "CD")
        self.assertEqual(res_two_pos["confidence"], 80.0)
        self.assertEqual(set(res_two_pos["positive_classes"]), {"CD", "HYP"})
        self.assertEqual(res_two_pos["decision_status"], "positive")
        self.assertFalse(res_two_pos["top_class_below_threshold"])

        # Case 2: All below threshold (NORM 62%, threshold is 88%).
        probs_all_below = {"CD": 10.0, "HYP": 10.0, "MI": 10.0, "NORM": 62.0, "STTC": 10.0}
        res_all_below = evaluate_thresholds(probs_all_below)
        self.assertEqual(res_all_below["primary_class"], "NORM")
        self.assertEqual(res_all_below["confidence"], 62.0)
        self.assertEqual(res_all_below["positive_classes"], [])
        self.assertEqual(res_all_below["decision_status"], "no_class_above_threshold")
        self.assertTrue(res_all_below["top_class_below_threshold"])

        # Case 3: Exactly equal to threshold (CD 70%, threshold is 70% -> counts as positive).
        probs_exact = {"CD": 70.0, "HYP": 10.0, "MI": 10.0, "NORM": 10.0, "STTC": 10.0}
        res_exact = evaluate_thresholds(probs_exact)
        self.assertEqual(res_exact["primary_class"], "CD")
        self.assertEqual(res_exact["confidence"], 70.0)
        self.assertEqual(res_exact["positive_classes"], ["CD"])
        self.assertEqual(res_exact["decision_status"], "positive")
        self.assertFalse(res_exact["top_class_below_threshold"])

        print("Test G (Synthetic evaluate_thresholds unit test) passed successfully!")


if __name__ == "__main__":
    unittest.main()
