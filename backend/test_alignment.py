from predict import ECGPredictor

predictor = ECGPredictor()

dummy = {
    "heart_rate": 70,
    "mean_rr": 0.92,
    "fake_feature": 999
}

aligned = predictor.align_features(dummy)

print("=" * 60)
print("Aligned Shape:", aligned.shape)
print("=" * 60)

print(aligned.head())

print()

print("Columns:", len(aligned.columns))