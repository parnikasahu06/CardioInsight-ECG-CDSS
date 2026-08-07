from model_loader import ModelLoader

loader = ModelLoader()

print("=" * 60)
print("Scaler features:", len(loader.scaler.feature_names_in_))
print("Model features :", loader.model.n_features_in_)
print("CSV features   :", len(loader.feature_names))
print("Imputer feats  :", len(loader.imputer.feature_names_in_))
print("=" * 60)