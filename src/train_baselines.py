import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV

from src.features import extract_features


def prepare_text_data(df):
    rows = []
    for _, row in df.iterrows():
        text = str(row["text"]) if pd.notna(row["text"]) else ""
        feats = extract_features(text)
        feats["label"] = row["label"]
        feats["text"] = text
        feats["source"] = row["source_dataset"]
        rows.append(feats)
    return pd.DataFrame(rows)


def train_tfidf_models(df):
    print("\n=== Training TF-IDF Models ===")

    texts = df["text"].fillna("").astype(str).tolist()
    labels = df["label"].tolist()

    tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=50000, sublinear_tf=True)
    X = tfidf.fit_transform(texts)

    label_map = {"safe": 0, "suspicious": 1, "dangerous": 2}
    y = np.array([label_map.get(l, 2) for l in labels])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    results = {}

    print("\n--- Logistic Regression ---")
    lr = LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", random_state=42)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    inv_map = {v: k for k, v in label_map.items()}
    target_names = [inv_map[i] for i in sorted(label_map.values())]
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
    results["logistic_regression"] = {"model": lr, "vectorizer": tfidf}

    print("--- Linear SVM ---")
    svm = LinearSVC(max_iter=2000, C=1.0, class_weight="balanced", random_state=42)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

    svm_calibrated = CalibratedClassifierCV(svm, cv=3)
    svm_calibrated.fit(X_train, y_train)
    results["linear_svm"] = {"model": svm_calibrated, "vectorizer": tfidf}

    return results


def train_bayesian_network(df):
    print("\n=== Training Bayesian Network ===")
    try:
        from pgmpy.models import DiscreteBayesianNetwork
        from pgmpy.estimators import BayesianEstimator, MaximumLikelihoodEstimator

        feature_cols = [c for c in df.columns if c not in ["text", "label", "source", "file_name", "has_file", "ext_archive"]]

        bool_cols = [c for c in feature_cols if df[c].dtype == bool or set(df[c].dropna().unique()).issubset({True, False, 0, 1})]
        if "n_links" in df.columns:
            df["has_many_links"] = df["n_links"] > 2
            bool_cols.append("has_many_links")

        df_bayes = df[bool_cols + ["label"]].copy()
        for col in bool_cols:
            df_bayes[col] = df_bayes[col].astype(str).map({"True": "yes", "False": "no", "0": "no", "1": "yes"})
        df_bayes["label"] = df_bayes["label"].astype(str)

        edges = [("label", col) for col in bool_cols]

        model = DiscreteBayesianNetwork(edges)
        model.fit(df_bayes, estimator=BayesianEstimator, prior_type="BDeu", equivalent_sample_size=5)

        print(f"  Nodes: {list(model.nodes())}")
        print(f"  Edges: {list(model.edges())}")
        results = {"bayesian_network": {"model": model, "feature_cols": bool_cols}}
        return results

    except Exception as e:
        print(f"  ERROR training Bayesian Network: {e}")
        return {}


def evaluate_models(df, tfidf_results, bayes_results):
    print("\n=== Evaluation ===")

    texts = df["text"].fillna("").astype(str).tolist()
    labels = df["label"].tolist()
    label_map = {"safe": 0, "suspicious": 1, "dangerous": 2}
    y = np.array([label_map.get(l, 2) for l in labels])

    if "logistic_regression" in tfidf_results:
        tfidf = tfidf_results["logistic_regression"]["vectorizer"]
        model = tfidf_results["logistic_regression"]["model"]
        X = tfidf.transform(texts)
        y_pred = model.predict(X)
        inv_map = {v: k for k, v in label_map.items()}
        target_names = [inv_map[i] for i in sorted(label_map.values())]
        print("\n--- Logistic Regression (Full Data) ---")
        print(classification_report(y, y_pred, target_names=target_names, zero_division=0))
        cm = confusion_matrix(y, y_pred)
        print(f"Confusion matrix:\n{cm}")

    if "linear_svm" in tfidf_results:
        tfidf = tfidf_results["linear_svm"]["vectorizer"]
        model = tfidf_results["linear_svm"]["model"]
        X = tfidf.transform(texts)
        y_pred = model.predict(X)
        inv_map = {v: k for k, v in label_map.items()}
        target_names = [inv_map[i] for i in sorted(label_map.values())]
        print("\n--- Linear SVM (Full Data) ---")
        print(classification_report(y, y_pred, target_names=target_names, zero_division=0))


def save_models(tfidf_results, bayes_results, out_dir="data/processed"):
    os.makedirs(out_dir, exist_ok=True)
    for name, data in tfidf_results.items():
        path = os.path.join(out_dir, f"{name}.pkl")
        with open(path, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved {name} to {path}")
    for name, data in bayes_results.items():
        path = os.path.join(out_dir, f"{name}.pkl")
        with open(path, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved {name} to {path}")


if __name__ == "__main__":
    from src.load_public import load_all

    df = load_all()
    if len(df) == 0:
        print("No data loaded. Exiting.")
        exit(1)

    enriched = prepare_text_data(df)
    print(f"\nEnriched dataset: {len(enriched)} rows, columns: {list(enriched.columns)}")

    tfidf_results = train_tfidf_models(df)
    bayes_results = train_bayesian_network(enriched)
    evaluate_models(df, tfidf_results, bayes_results)
    save_models(tfidf_results, bayes_results)
    print("\nDone!")
