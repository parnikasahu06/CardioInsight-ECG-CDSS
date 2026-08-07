from model_loader import ModelLoader

loader = ModelLoader()

print("=" * 60)
print("Model Loaded Successfully")
print("=" * 60)

print("Model expects:", loader.model.n_features_in_)
print("Feature names:", len(loader.feature_names))

print(type(self.model))