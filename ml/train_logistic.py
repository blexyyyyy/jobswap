# ml/train_logistic.py
from __future__ import annotations

from pathlib import Path
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

from ml.build_dataset import build_dataset
from ml.features import FEATURE_KEYS

MODEL_PATH = Path("ml/models/logreg_job_match.pkl")


def main():
    df = build_dataset()
    if df.empty:
        print("[ML] No training data available. Aborting training.")
        return

    # Ensure all feature columns exist
    for key in FEATURE_KEYS:
        if key not in df.columns:
            df[key] = 0.0

    X = df[FEATURE_KEYS].values
    y = df["label"].values

    if len(df) < 10:
        print(f"[ML] Only {len(df)} samples. Too small for meaningful model, training anyway.")
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        # Not enough class variety
        X_train, X_test, y_train, y_test = X, X, y, y

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    try:
        y_proba = clf.predict_proba(X_test)[:, 1]
    except Exception:
        y_proba = None

    acc = accuracy_score(y_test, y_pred)
    print(f"[ML] Accuracy: {acc:.4f}")
    if y_proba is not None:
        try:
            auc = roc_auc_score(y_test, y_proba)
            print(f"[ML] ROC AUC: {auc:.4f}")
        except ValueError:
            print("[ML] ROC AUC not defined (single-class test set).")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as f:
        pickle.dump(
            {
                "model": clf,
                "feature_order": FEATURE_KEYS,
            },
            f,
        )
    print(f"[ML] Saved logistic model to {MODEL_PATH}")


if __name__ == "__main__":
    main()