# ml/train_model.py

import os
import pickle
import sqlite3

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

DB_PATH = "database/jobmatcher.db"
MODEL_PATH = os.path.join("ml", "match_model.pkl")

FEATURE_COLUMNS = ["semantic_sim", "skill_overlap", "exp_gap", "location_match"]


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions", conn)
    conn.close()

    # Basic sanity filter
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])
    if df.empty:
        raise RuntimeError("No interaction data available to train on.")

    X = df[FEATURE_COLUMNS]
    y = df["label"].astype(int)

    return X, y


def train():
    X, y = load_data()

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Evaluate
    if len(set(y_val)) > 1:
        probs = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, probs)
        print(f"AUC: {auc:.3f}")
    else:
        print("Warning: Only one class in validation set; skipping AUC.")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
