import numpy as np
import pandas as pd

from predict import ECGPredictor

predictor = ECGPredictor()

dummy = {
    "heart_rate": 70,
    "mean_rr": 0.92
}

aligned = predictor.align_features(dummy)

print("=" * 60)
print("NaNs Before:")
print(aligned.isna().sum().sum())

imputed = predictor.apply_imputer(aligned)

print("=" * 60)
print("NaNs After:")
print(imputed.isna().sum().sum())

print("=" * 60)
print(imputed.head())