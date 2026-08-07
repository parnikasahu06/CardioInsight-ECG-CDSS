import wfdb
import pandas as pd

from feature_extractor import FeatureExtractor

# Load one sample ECG
record = wfdb.rdrecord(
    "data/ptb-xl/records500/00000/00001_hr"
)

signal = record.p_signal

# Create extractor
extractor = FeatureExtractor()

# Extract features
features = extractor.extract_features(signal)

from predict import ECGPredictor

predictor = ECGPredictor()

aligned = predictor.align_features(features)

print("=" * 60)
print("Total NaNs:", aligned.isna().sum().sum())

missing = aligned.columns[aligned.isna().any()]

print("Columns with NaNs:", len(missing))
print("\nMissing Feature Names:\n")

for f in missing:
    print(f)

print("=" * 60)

print("=" * 60)
print("Feature Extraction Successful")
print("=" * 60)

print("Type:", type(features))
print("Number of Features:", len(features))

print("\nFirst 20 Features:\n")

for i, (k, v) in enumerate(features.items()):
    print(k, ":", v)

    if i == 19:
        break
