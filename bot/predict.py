import os
import re
import pickle
import numpy as np
from scipy.sparse import hstack, csr_matrix
from src.features import (
    extract_features, analyze_message,
    URGENCY_EN, URGENCY_KM, MONEY_BAIT_EN, MONEY_BAIT_KM,
    CREDENTIAL_ASK, PAYMENT_SCAM_EN, FAMILY_SCAM_EN, FAMILY_SCAM_KM,
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
_hybrid_model = None


def _load_hybrid_model():
    global _hybrid_model
    if _hybrid_model is None:
        path = os.path.join(MODEL_DIR, "hybrid_model.pkl")
        if os.path.exists(path):
            with open(path, "rb") as f:
                _hybrid_model = pickle.load(f)
    return _hybrid_model


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
    text_lower = text.lower()
    reasons = []
    if any(w in text_lower for w in URGENCY_EN + URGENCY_KM):
        reasons.append("Urgency language detected")
    if any(w in text_lower for w in MONEY_BAIT_EN + MONEY_BAIT_KM):
        reasons.append("Money or prize bait detected")
    if any(w in text_lower for w in CREDENTIAL_ASK):
        reasons.append("Asks for login credentials or OTP")
    if any(w in text_lower for w in PAYMENT_SCAM_EN):
        reasons.append("Payment scam pattern detected")
    if any(w in text_lower for w in FAMILY_SCAM_EN + FAMILY_SCAM_KM):
        reasons.append("Family emergency scam pattern detected")
    return reasons


def predict_ensemble(text):
    features = extract_features(text)
    kw_reasons = _extract_keyword_reasons(text)
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
        except Exception:
            pass

    kw_score = len(kw_reasons) * 25

    if kw_score >= 50:
        final_score = max(kw_score, ml_score + 20)
    elif kw_score >= 25:
        final_score = max(kw_score, ml_score + 10)
    elif ml_score >= 70:
        final_score = ml_score
    else:
        final_score = 0

    if final_score >= 60:
        risk_level = "dangerous"
    elif final_score >= 25:
        risk_level = "suspicious"
    else:
        risk_level = "safe"

    all_reasons = list(kw_reasons)
    if features.get("ext_exec"):
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
            "ml_prediction": ml_pred,
            "ml_confidence": ml_confidence,
            "keyword_reasons": kw_reasons,
        },
    }
