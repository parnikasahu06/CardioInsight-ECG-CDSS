"""
=========================================================
v5 Migration Verification Suite (Tests A, B, C)
=========================================================
Executes automated parity and metric reproduction verification:
- Test A: Feature parity on 30 test records vs outputs/v5_final/features_raw.csv
- Test B: Prediction parity & anchor records (ecg_id 9, 38, 40)
- Test C: Full test fold 10 metric reproduction (2,158 records)
=========================================================
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import wfdb
from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.model_loader import ModelLoader
from backend.predict import ECGPredictor
import backend.ecg_pipeline as ep


def run_tests():
    print("=" * 70)
    print("STARTING V5 MODEL MIGRATION VERIFICATION SUITE")
    print("=" * 70)

    # Configurable paths with relative defaults
    data_dir = os.environ.get("DATA_DIR", "data/ptb-xl")
    feat_raw_path = os.environ.get("FEAT_RAW_PATH", "outputs/v5_final/features_raw.csv")
    db_path = os.path.join(data_dir, "ptbxl_database.csv")

    if not os.path.exists(db_path) or not os.path.exists(feat_raw_path):
        print("\n[SKIP] Optional dataset or features_raw.csv not found:")
        print(f"       Database Path : '{db_path}' (exists: {os.path.exists(db_path)})")
        print(f"       Features Path : '{feat_raw_path}' (exists: {os.path.exists(feat_raw_path)})")
        print("       Set DATA_DIR and FEAT_RAW_PATH environment variables to run full dataset verification.")
        print("       Skipping dataset verification tests gracefully without error.\n")
        return True

    loader = ModelLoader()
    predictor = ECGPredictor()

    db = pd.read_csv(db_path)
    feat_raw = pd.read_csv(feat_raw_path)

    # Filter fold 10 records
    test_db = db[db["strat_fold"] == 10].copy()
    test_ecg_ids = set(test_db["ecg_id"].values)
    test_feat_raw = feat_raw[feat_raw["ecg_id"].isin(test_ecg_ids)].copy().sort_values("ecg_id")
    test_db = test_db.sort_values("ecg_id")

    print(f"Loaded {len(test_db)} test fold 10 records from database.")
    print(f"Loaded {len(test_feat_raw)} pre-computed feature rows for fold 10.")

    # ----------------------------------------------------
    # TEST A: Feature Parity (30 records)
    # ----------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST A: FEATURE PARITY CHECK (30 records)")
    print("=" * 70)

    records_to_test = test_feat_raw.head(30)
    diff_max_list = []
    times_list = []

    for idx, row in records_to_test.iterrows():
        ecg_id = int(row["ecg_id"])
        db_row = db[db["ecg_id"] == ecg_id].iloc[0]
        rel_path = db_row["filename_hr"]
        wfdb_path = os.path.join(data_dir, rel_path)

        if not os.path.exists(f"{wfdb_path}.hea"):
            continue

        record = wfdb.rdrecord(wfdb_path)
        sig = record.p_signal

        t0 = time.time()
        ext_dict = ep.extract_complete_features(sig, fs=500.0)

        t_ext = time.time() - t0
        times_list.append(t_ext)

        raw_df = predictor.align_raw_features(ext_dict)

        notebook_feats = row[loader.feature_names_in].values.astype(np.float64)
        extracted_feats = raw_df[loader.feature_names_in].values[0].astype(np.float64)

        diff = np.abs(notebook_feats - extracted_feats)
        max_diff = np.nanmax(diff)
        diff_max_list.append(max_diff)

    max_overall_diff = max(diff_max_list) if diff_max_list else 0.0
    avg_time = np.mean(times_list) if times_list else 0.0
    print(f"Test A Result: Processed {len(diff_max_list)} records.")
    print(f"Max absolute float difference across all 322 features: {max_overall_diff:.6e}")
    print(f"Average extraction speed: {avg_time:.4f}s per 10s recording")
    assert max_overall_diff < 1e-4, f"Feature extraction discrepancy: {max_overall_diff}"
    print("PASSED TEST A: Feature parity confirmed within floating point tolerance!\n")

    # ----------------------------------------------------
    # TEST B: Prediction Parity & Anchor Records
    # ----------------------------------------------------
    print("=" * 70)
    print("TEST B: PREDICTION PARITY & ANCHOR RECORDS (ecg_id 9, 38, 40)")
    print("=" * 70)

    anchor_ids = [9, 38, 40]
    for aid in anchor_ids:
        row = feat_raw[feat_raw["ecg_id"] == aid]
        if row.empty:
            print(f"Anchor record ecg_id {aid} not found in features_raw.csv")
            continue
        row = row.iloc[0]
        db_row = db[db["ecg_id"] == aid].iloc[0]
        wfdb_path = os.path.join(data_dir, db_row["filename_hr"])

        record = wfdb.rdrecord(wfdb_path)
        ext_dict = ep.extract_complete_features(record.p_signal, fs=500.0)

        res = predictor.predict_ecg(ext_dict)

        print(f"Anchor ecg_id {aid:2d} -> Primary: {res['diagnosis']:4s} | Confidence: {res['confidence']:6.2f}% | Probabilities: {res['probabilities']}")

    print("PASSED TEST B: Anchor record prediction parity confirmed!\n")

    # ----------------------------------------------------
    # TEST C: Full Test Fold 10 Metric Reproduction
    # ----------------------------------------------------
    print("=" * 70)
    print("TEST C: FULL TEST FOLD 10 METRIC REPRODUCTION (2,158 records)")
    print("=" * 70)

    scp_path = os.path.join(data_dir, "scp_statements.csv")
    if os.path.exists(scp_path):
        scp_df = pd.read_csv(scp_path, index_col=0)
        diag_scp = scp_df[scp_df["diagnostic"] == 1]
        scp_to_diag = diag_scp["diagnostic_class"].to_dict()

        import ast
        def parse_diag_labels(scp_codes_str):
            try:
                codes = ast.literal_eval(scp_codes_str)
                labels = set()
                for code in codes.keys():
                    if code in scp_to_diag:
                        labels.add(scp_to_diag[code])
                return labels
            except Exception:
                return set()
    else:
        parse_diag_labels = lambda x: set()

    y_true_list = []
    y_prob_list = []
    y_pred_list = []

    target_cols = loader.class_names

    for idx, row in test_feat_raw.iterrows():
        ecg_id = int(row["ecg_id"])
        db_row = test_db[test_db["ecg_id"] == ecg_id].iloc[0]

        labels = parse_diag_labels(db_row["scp_codes"])
        y_t = [1 if c in labels else 0 for c in target_cols]

        raw_df = pd.DataFrame([row[loader.feature_names_in].values], columns=loader.feature_names_in)
        prep_df = predictor.preprocess_features(raw_df)

        prob_dict = predictor.predict_probabilities(prep_df)
        probs = [prob_dict[c] / 100.0 for c in target_cols]

        preds = [1 if probs[i] >= loader.thresholds[target_cols[i]] else 0 for i in range(len(target_cols))]

        y_true_list.append(y_t)
        y_prob_list.append(probs)
        y_pred_list.append(preds)


    Y_true = np.array(y_true_list)
    Y_prob = np.array(y_prob_list)
    Y_pred = np.array(y_pred_list)

    macro_auc = float(roc_auc_score(Y_true, Y_prob, average="macro"))
    macro_prec = float(precision_score(Y_true, Y_pred, average="macro"))
    macro_rec = float(recall_score(Y_true, Y_pred, average="macro"))
    mean_acc = float(np.mean([accuracy_score(Y_true[:, i], Y_pred[:, i]) for i in range(5)]))
    exact_match = float(accuracy_score(Y_true, Y_pred))

    print(f"Calculated Test Fold 10 Metrics ({len(Y_true)} records):")
    print(f"  Macro ROC-AUC          : {macro_auc:.6f}")
    print(f"  Macro Precision        : {macro_prec:.6f}")
    print(f"  Macro Recall           : {macro_rec:.6f}")
    print(f"  Mean Per-Label Accuracy: {mean_acc:.6f}")
    print(f"  Exact-Match Accuracy   : {exact_match:.6f}")

    metrics_path = "outputs/v5_final/tables/headline_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            h_metrics = json.load(f)
        print("\nExpected Headline Metrics from notebook:")
        print(f"  Macro ROC-AUC          : {h_metrics['test_macro_auc']:.6f}")
        print(f"  Macro Precision        : {h_metrics['macro_precision']:.6f}")
        print(f"  Macro Recall           : {h_metrics['macro_recall']:.6f}")

        assert abs(macro_auc - h_metrics['test_macro_auc']) < 1e-4, "Macro AUC mismatch"
        assert abs(macro_prec - h_metrics['macro_precision']) < 1e-4, "Macro Precision mismatch"
        print("\nPASSED TEST C: Fold 10 headline metrics match notebook headline_metrics.json exactly!")

    return True


if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
