import pandas as pd
import wfdb

from feature_extractor import FeatureExtractor

# Load ECG
record = wfdb.rdrecord(
    "data/ptb-xl/records500/00000/00001_hr"
)

signal = record.p_signal

# Extract features
extractor = FeatureExtractor()
features = extractor.extract_features(signal)

generated = list(features.keys())

trained = pd.read_csv(
    "models/trained/feature_names.csv"
)

# Handle CSV with one column
trained = trained.iloc[:, 0].tolist()

print("=" * 60)
print("Generated Features :", len(generated))
print("Trained Features   :", len(trained))
print("=" * 60)

missing = sorted(set(trained) - set(generated))
extra = sorted(set(generated) - set(trained))

print("\nMissing Features:", len(missing))
for f in missing:
    print(f)

print("\nExtra Features:", len(extra))
for f in extra:
    print(f)