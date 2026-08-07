print("RUNNING NEW VERSION")
import wfdb

from backend.feature_extractor import FeatureExtractor
from backend.predict import ECGPredictor

print("=" * 60)
print("Loading ECG...")
print("=" * 60)

record = wfdb.rdrecord(
    "data/ptb-xl/records500/00000/00001_hr"
)

signal = record.p_signal

print("Extracting Features...")

extractor = FeatureExtractor()

features = extractor.extract_features(signal)

print("Total extracted:", len(features))

predictor = ECGPredictor()

print("\nAligning Features...")
aligned = predictor.align_features(features)

print(aligned.shape)

print("\nApplying Imputer...")
import numpy as np

print("="*60)
print("Checking aligned features")
print("="*60)

print("NaNs :", aligned.isna().sum().sum())
print("Infs :", np.isinf(aligned.values).sum())

inf_cols = aligned.columns[np.isinf(aligned.values).any(axis=0)]

print("\nColumns containing infinity:")

for c in inf_cols:
    print(c)

print("\nInfinite values:")

for c in inf_cols:
    print(c, "=", aligned.loc[0, c])

imputed = predictor.apply_imputer(aligned)

print(imputed.shape)

print("\nApplying Scaler...")
scaled = predictor.apply_scaler(imputed)

print(scaled.shape)

print("\nPredicting...")

import numpy as np

print("=" * 60)
print("Checking scaled features")
print("=" * 60)

print("NaNs :", scaled.isna().sum().sum())
print("Infs :", np.isinf(scaled.values).sum())

inf_cols = scaled.columns[np.isinf(scaled.values).any(axis=0)]

print("\nColumns containing inf:")
for c in inf_cols:
    print(c)

prediction = predictor.predict(scaled)
print("\nPredicted labels:")
print(prediction)

print("\nProbabilities...")
prob = predictor.predict_proba(scaled)
print(prob)