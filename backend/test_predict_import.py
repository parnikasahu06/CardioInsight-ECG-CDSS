import wfdb

from feature_extractor import FeatureExtractor
from predict import ECGPredictor

# Load one ECG
record = wfdb.rdrecord(
    "data/ptb-xl/records500/00000/00001_hr"
)

signal = record.p_signal

extractor = FeatureExtractor()
features = extractor.extract_features(signal)

predictor = ECGPredictor()

prediction = predictor.predict(features)

print(prediction)