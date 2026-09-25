import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from scipy.sparse import hstack, csr_matrix

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.features import (
    extract_features, URGENCY_EN, URGENCY_KM, MONEY_BAIT_EN, MONEY_BAIT_KM,
    CREDENTIAL_ASK, PAYMENT_SCAM_EN, FAMILY_SCAM_EN, FAMILY_SCAM_KM,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MODEL_DIR = DATA_DIR


def get_keyword_features(text):
    text_lower = text.lower()
    features = []
    features.append(1 if any(w in text_lower for w in URGENCY_EN + URGENCY_KM) else 0)
    features.append(1 if any(w in text_lower for w in MONEY_BAIT_EN + MONEY_BAIT_KM) else 0)
    features.append(1 if any(w in text_lower for w in CREDENTIAL_ASK) else 0)
    features.append(1 if any(w in text_lower for w in PAYMENT_SCAM_EN) else 0)
    features.append(1 if any(w in text_lower for w in FAMILY_SCAM_EN + FAMILY_SCAM_KM) else 0)
    features.append(1 if "http" in text_lower or "www." in text_lower else 0)
    features.append(1 if "$" in text or "dollar" in text_lower or "ដុល្លារ" in text else 0)
    features.append(1 if any(c.isdigit() for c in text) else 0)
    features.append(len(text))
    features.append(text.count("!"))
    features.append(text.count("?"))
    features.append(text.count("$"))
    return features


def extract_keyword_reasons(text):
    text_lower = text.lower()
    reasons = []
    if any(w in text_lower for w in URGENCY_EN + URGENCY_KM):
        reasons.append("urgency")
    if any(w in text_lower for w in MONEY_BAIT_EN + MONEY_BAIT_KM):
        reasons.append("money_bait")
    if any(w in text_lower for w in CREDENTIAL_ASK):
        reasons.append("credential_ask")
    if any(w in text_lower for w in PAYMENT_SCAM_EN):
        reasons.append("payment_scam")
    if any(w in text_lower for w in FAMILY_SCAM_EN + FAMILY_SCAM_KM):
        reasons.append("family_scam")
    return reasons


def train():
    print("Loading datasets...")

    combined = pd.read_csv(os.path.join(DATA_DIR, "..", "raw", "combined_spam_ham.csv"), encoding="utf-8")
    combined["label"] = combined["label"].map({"spam": 1, "ham": 0})
    combined = combined.dropna(subset=["text", "label"])
    combined["label"] = combined["label"].astype(int)

    all_data = combined

    print(f"Total: {len(all_data)} messages (spam={sum(all_data['label']==1)}, ham={sum(all_data['label']==0)})")

    print("Creating TF-IDF features...")
    tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2, max_df=0.95, sublinear_tf=True)
    X_tfidf = tfidf.fit_transform(all_data["text"])

    print("Creating keyword features...")
    kw_features = np.array([get_keyword_features(t) for t in all_data["text"]])
    X_kw = csr_matrix(kw_features)

    X_combined = hstack([X_tfidf, X_kw])
    y = all_data["label"].values

    X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42, stratify=y)

    print(f"\nTraining Logistic Regression (TF-IDF + Keywords)...")
    lr = LogisticRegression(C=1.0, max_iter=5000, random_state=42)
    lr.fit(X_train, y_train)
    lr_acc = accuracy_score(y_test, lr.predict(X_test))
    print(f"LR Accuracy: {lr_acc:.1%}")
    print(classification_report(y_test, lr.predict(X_test), target_names=["ham", "scam"]))

    print(f"\nTraining Linear SVM (TF-IDF + Keywords)...")
    svm = LinearSVC(C=0.5, max_iter=2000, random_state=42)
    svm.fit(X_train, y_train)
    svm_acc = accuracy_score(y_test, svm.predict(X_test))
    print(f"SVM Accuracy: {svm_acc:.1%}")
    print(classification_report(y_test, svm.predict(X_test), target_names=["ham", "scam"]))

    model_data = {
        "tfidf": tfidf,
        "lr": lr,
        "svm": svm,
        "lr_accuracy": lr_acc,
        "svm_accuracy": svm_acc,
    }

    output_path = os.path.join(MODEL_DIR, "hybrid_model.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(model_data, f)
    print(f"\nModel saved: {output_path}")
    print(f"  LR:  {lr_acc:.1%}")
    print(f"  SVM: {svm_acc:.1%}")

    return model_data


if __name__ == "__main__":
    train()
