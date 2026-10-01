"""
=========================================================
Live Server Flow & Timing Test
=========================================================
Tests real HTTP requests against the live running FastAPI server:
1. GET http://127.0.0.1:8000/health (verifies backend status green)
2. POST http://127.0.0.1:8000/predict for records 9, 38, 40
3. Measures end-to-end network request duration & SHAP execution time
=========================================================
"""

import time
import requests
import os

BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
DATA_DIR = os.environ.get("DATA_DIR", "data/ptb-xl")
RECORD_DIR = os.path.join(DATA_DIR, "records500/00000")

def test_health():
    print("Testing GET /health...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
    except Exception as e:
        print(f"[SKIP] Backend server is not reachable at {BASE_URL}. Ensure uvicorn server is running.")
        return False

    print("Status Code:", resp.status_code)
    data = resp.json()
    print("Health Payload:", data)
    assert resp.status_code == 200
    assert data.get("status") == "healthy"
    assert data.get("model_loaded") is True
    print("-> Backend Status is GREEN (Online & Ready)!\n")
    return True

def test_record_upload(record_id):
    hea_path = os.path.join(RECORD_DIR, f"{record_id}_hr.hea")
    dat_path = os.path.join(RECORD_DIR, f"{record_id}_hr.dat")

    if not os.path.exists(hea_path) or not os.path.exists(dat_path):
        print(f"[SKIP] Record files for {record_id}_hr not found at '{hea_path}'. Set DATA_DIR environment variable.")
        return None

    print(f"--- Uploading Record {record_id}_hr (.hea + .dat) ---")
    
    t0 = time.perf_counter()
    with open(hea_path, "rb") as f_hea, open(dat_path, "rb") as f_dat:
        files = {
            "hea_file": (f"{record_id}_hr.hea", f_hea, "text/plain"),
            "dat_file": (f"{record_id}_hr.dat", f_dat, "application/octet-stream")
        }
        resp = requests.post(f"{BASE_URL}/predict", files=files)
    t_total = time.perf_counter() - t0

    print("HTTP Status Code:", resp.status_code)
    assert resp.status_code == 200, f"Failed: {resp.text}"

    data = resp.json()
    print(f"Primary Diagnosis  : {data.get('diagnosis')}")
    print(f"Confidence         : {data.get('confidence')}%")
    print(f"Risk Tier          : {data.get('risk_level')}")
    print(f"Probabilities      : {data.get('probabilities')}")
    print(f"Top SHAP Feature   : {data.get('top_features')[0]['clean_name']} (SHAP: {data.get('top_features')[0]['SHAP']:+.4f})")
    print(f"Total API Time     : {t_total:.4f} seconds (including 322-feature extraction, XGBoost inference, and SHAP explainability)")
    print("-" * 60 + "\n")
    return t_total

if __name__ == "__main__":
    healthy = test_health()
    if healthy:
        records = ["00009", "00038", "00040"]
        times = []
        for r in records:
            t = test_record_upload(r)
            if t is not None:
                times.append(t)

        if times:
            avg_time = sum(times) / len(times)
            print(f"Summary across anchor records {records}:")
            print(f"Average Total Processing Time: {avg_time:.4f}s (Min: {min(times):.4f}s, Max: {max(times):.4f}s)")
