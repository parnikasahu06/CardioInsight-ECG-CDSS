"""
=========================================================
Bundle Re-saver & Verification Script
=========================================================
Solves the pickle trap by importing custom classes from backend.ecg_pipeline,
injecting them into sys.modules['__main__'] prior to loading the original
outputs/v5_final/ecg_model_bundle.pkl, and then re-saving a backend-compatible
copy to models/trained/v5_ecg_model_bundle.pkl.

The original file in outputs/v5_final/ remains 100% untouched.
=========================================================
"""

import os
import sys
import joblib

# Inject backend directory into sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import backend.ecg_pipeline as ep

# --------------------------------------------------------
# Inject classes into __main__ for unpickling original bundle
# --------------------------------------------------------
main_dict = sys.modules["__main__"].__dict__
main_dict["MissingFilter"] = ep.MissingFilter
main_dict["QuantileClipper"] = ep.QuantileClipper
main_dict["CorrelationPruner"] = ep.CorrelationPruner
main_dict["XGBMultiLabel"] = ep.XGBMultiLabel
main_dict["XGBClassifierChain"] = ep.XGBClassifierChain

SRC_BUNDLE = "outputs/v5_final/ecg_model_bundle.pkl"
DST_BUNDLE = "models/trained/v5_ecg_model_bundle.pkl"

def main():
    print(f"Loading bundle from {SRC_BUNDLE}...")
    bundle = joblib.load(SRC_BUNDLE)
    print("Bundle loaded successfully!")

    print("\n--- Bundle Metadata Verification ---")
    print(f"Model Name            : {bundle.get('model_name')}")
    print(f"Class Names           : {bundle.get('class_names')}")
    print(f"Active Thresholds     : {bundle.get('thresholds')}")
    print(f"Thresholds (F1)       : {bundle.get('thresholds_f1')}")
    print(f"Thresholds (Precision): {bundle.get('thresholds_precision_target')}")
    print(f"Raw Features In       : {len(bundle.get('feature_names_in'))}")
    print(f"Model Features Out    : {len(bundle.get('feature_names_model'))}")
    print(f"Sampling Rate         : {bundle.get('sampling_rate')}")
    print(f"Use Demographics      : {bundle.get('use_demographics')}")
    print(f"Feature Version       : {bundle.get('feature_version')}")

    os.makedirs(os.path.dirname(DST_BUNDLE), exist_ok=True)
    print(f"\nRe-saving backend model bundle to {DST_BUNDLE}...")
    joblib.dump(bundle, DST_BUNDLE)
    print("Local backend bundle re-saved successfully!")

if __name__ == "__main__":
    main()
