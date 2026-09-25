import os
import re
import logging
import pickle
import numpy as np
from scipy.sparse import hstack, csr_matrix
from src.features import (
    extract_features, analyze_message, money_lure, has_keyword,
    URGENCY_EN, URGENCY_KM, MONEY_BAIT_EN, MONEY_BAIT_KM,
    CREDENTIAL_ASK, PAYMENT_SCAM_EN, FAMILY_SCAM_EN, FAMILY_SCAM_KM,
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
_hybrid_model = None

logger = logging.getLogger(__name__)

_KW_REASON_ALIAS = {
    "Urgency language detected": "Message uses urgency language",
    "Money amount lure detected (send small, promised much larger return)":
        "Money amount lure (send small amount, promised much larger return)",
}

_KW_REASON_WEIGHT = {
    "Urgency language detected": 15,
    "Money or prize bait detected": 15,
    "Asks for login credentials or OTP": 25,
    "Payment scam pattern detected": 25,
    "Family emergency scam pattern detected": 25,
    "Money amount lure detected (send small, promised much larger return)": 30,
}


def _load_hybrid_model():
    global _hybrid_model
    if _hybrid_model is None:
        path = os.path.join(MODEL_DIR, "hybrid_model.pkl")
        if os.path.exists(path):
            with open(path, "rb") as f:
                _hybrid_model = pickle.load(f)
    return _hybrid_model


_TFIDF_MODELS = {}
_TFIDF_LABELS = {0: "safe", 1: "suspicious", 2: "dangerous"}


def _load_tfidf_model(name):
    if name not in _TFIDF_MODELS:
        path = os.path.join(MODEL_DIR, f"{name}.pkl")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            _TFIDF_MODELS[name] = pickle.load(f)
    return _TFIDF_MODELS[name]


def predict_tfidf(text, model_name):
    """Standalone TF-IDF model prediction: 'safe' | 'suspicious' | 'dangerous'."""
    model = _load_tfidf_model(model_name)
    if not model:
        return "unknown"
    try:
        X = model["vectorizer"].transform([text])
        pred = int(model["model"].predict(X)[0])
        return _TFIDF_LABELS.get(pred, "unknown")
    except Exception as e:
        logger.warning(f"predict_tfidf({model_name}) failed: {e}")
        return "unknown"


def _get_keyword_features(text):
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


def _extract_keyword_reasons(text):
    reasons = []
    if has_keyword(text, URGENCY_EN + URGENCY_KM):
        reasons.append("Urgency language detected")
    if has_keyword(text, MONEY_BAIT_EN + MONEY_BAIT_KM):
        reasons.append("Money or prize bait detected")
    if has_keyword(text, CREDENTIAL_ASK):
        reasons.append("Asks for login credentials or OTP")
    if has_keyword(text, PAYMENT_SCAM_EN):
        reasons.append("Payment scam pattern detected")
    if has_keyword(text, FAMILY_SCAM_EN + FAMILY_SCAM_KM):
        reasons.append("Family emergency scam pattern detected")
    if money_lure(text):
        reasons.append("Money amount lure detected (send small, promised much larger return)")
    return reasons


def predict_ensemble(text):
    features = extract_features(text)
    kw_reasons = _extract_keyword_reasons(text)
    rule = analyze_message(text)
    model = _load_hybrid_model()

    ml_score = 0
    ml_pred = "unknown"
    ml_confidence = 0

    if model:
        try:
            tfidf = model["tfidf"]
            lr = model["lr"]
            svm = model["svm"]

            X_tfidf = tfidf.transform([text])
            kw_feats = np.array([_get_keyword_features(text)])
            X_kw = csr_matrix(kw_feats)
            X_combined = hstack([X_tfidf, X_kw])

            lr_prob = float(lr.predict_proba(X_combined)[0][1])
            lr_pred = int(lr.predict(X_combined)[0])
            svm_pred = int(svm.predict(X_combined)[0])

            ml_score = int(lr_prob * 100)
            ml_pred = "scam" if lr_pred == 1 else "safe"
            ml_confidence = int(lr_prob * 100)
        except Exception as e:
            logger.warning(f"ML scoring failed: {e}")

    kw_score = sum(_KW_REASON_WEIGHT.get(r, 25) for r in kw_reasons)
    has_signal = kw_score >= 25 or rule["score"] >= 15

    if not has_signal:
        final_score = 0
    elif kw_score >= 45:
        final_score = max(kw_score, ml_score + 20, rule["score"])
    elif kw_score >= 25:
        final_score = max(kw_score, ml_score + 10, rule["score"])
    else:
        final_score = max(rule["score"], ml_score if ml_score >= 70 else 0)

    if rule["risk_level"] == "dangerous" and final_score < 60:
        final_score = 60

    if final_score >= 60:
        risk_level = "dangerous"
    elif final_score >= 25:
        risk_level = "suspicious"
    else:
        risk_level = "safe"

    all_reasons = list(rule["reasons"])
    for r in kw_reasons:
        alias = _KW_REASON_ALIAS.get(r, r)
        if r not in all_reasons and alias not in all_reasons:
            all_reasons.append(r)
    if features.get("ext_exec") and not any("executable" in r for r in all_reasons):
        all_reasons.append("File has an executable extension")
    if ml_pred == "scam" and ml_confidence > 70:
        all_reasons.append(f"ML model detected scam ({ml_confidence}% confidence)")

    if not all_reasons:
        all_reasons = ["No specific risks detected"]

    return {
        "risk_level": risk_level,
        "score": min(final_score, 100),
        "reasons": all_reasons,
        "ml_predictions": {
            "keyword_score": kw_score,
            "ml_score": ml_score,
            "rule_score": rule["score"],
            "ml_prediction": ml_pred,
            "ml_confidence": ml_confidence,
            "keyword_reasons": kw_reasons,
        },
    }
