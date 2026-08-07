import wfdb

from feature_extractor import FeatureExtractor
from predict import ECGPredictor


record = wfdb.rdrecord(
    "data/ptb-xl/records500/00000/00001_hr"
)

signal = record.p_signal


extractor = FeatureExtractor()

features = extractor.extract_features(signal)


predictor = ECGPredictor()

result = predictor.predict_ecg(features)


print("="*60)
print("Prediction")
print("="*60)

print(result["prediction"])

print()

print("="*60)
print("Probabilities")
print("="*60)

print(result["probabilities"])