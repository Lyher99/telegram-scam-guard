import os
import pickle
import numpy as np
from bot.url_features import extract_url_features, get_feature_names, SAFE_DOMAINS
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "url_models.pkl")

_models = None


def _load_models():
    global _models
    if _models is None:
        try:
            with open(MODEL_PATH, "rb") as f:
                _models = pickle.load(f)
        except Exception:
            _models = {}
    return _models


def predict_url(url):
    models = _load_models()
    if not models:
        return {"error": "No model loaded"}

    features = extract_url_features(url)
    if features is None:
        return {"error": "Invalid URL"}

    if features.get("is_known_safe_domain") == 1:
        return {"ensemble": 0, "avg_prob": 0.0, "rule": "known_safe_domain"}

    feature_names = get_feature_names()
    X = np.array([[features[f] for f in feature_names]])

    results = {}

    if "lr_features" in models:
        results["lr_features"] = int(models["lr_features"].predict(X)[0])
        results["lr_features_prob"] = round(float(models["lr_features"].predict_proba(X)[0][1]), 4)

    if "svm_features" in models:
        results["svm_features"] = int(models["svm_features"].predict(X)[0])

    votes = [
        results.get("lr_features", 0),
        results.get("svm_features", 0),
    ]
    results["ensemble"] = 1 if sum(votes) >= 2 else 0

    probs = [results.get("lr_features_prob", 0)]
    results["avg_prob"] = round(sum(probs) / len(probs), 4)

    return results
