# recommendation/train_model.py
import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def train(dataset_path: str):
    # 1. Load dataset (already standardized/normalized CSV)
    df = pd.read_csv(dataset_path)

    # 2. Features + target
    X = df.drop(columns=["Tier"])
    y = df["Tier"]

    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train LightGBM
    model = lgb.LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=-1,
        random_state=42
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"✅ Accuracy: {acc:.3f}")
    print(classification_report(y_test, preds))

    # 6. Save model + feature columns
    joblib.dump(model, ARTIFACTS_DIR / "classifier.pkl")
    joblib.dump(list(X.columns), ARTIFACTS_DIR / "features.pkl")
    print("📦 Model + features saved to artifacts/")

if __name__ == "__main__":
    train("data/normalized_dataset.csv")  # adjust path
