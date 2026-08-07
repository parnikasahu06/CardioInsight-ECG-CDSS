from model_loader import ModelLoader

loader = ModelLoader()

print("=" * 60)
print("Number of imputer features:")
print(len(loader.imputer.feature_names_in_))

print("=" * 60)
print("First 20 feature names:\n")

for f in loader.imputer.feature_names_in_[:20]:
    print(f)

print("=" * 60)

csv_features = set(loader.feature_names)
imputer_features = set(loader.imputer.feature_names_in_)

print("CSV:", len(csv_features))
print("Imputer:", len(imputer_features))

print("\nMissing from CSV:")
for f in sorted(imputer_features - csv_features):
    print(f)

print("\nExtra in CSV:")
for f in sorted(csv_features - imputer_features):
    print(f)