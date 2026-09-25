import os
import pandas as pd
import pickle
import logging
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_sms_spam():
    path = os.path.join(RAW_DIR, "sms_spam.csv")
    df = pd.read_csv(path)
    df["label"] = df["label"].map({"spam": 1, "ham": 0})
    df = df.rename(columns={"text": "message"})
    return df[["message", "label"]]


def load_khmer_scam():
    path = os.path.join(RAW_DIR, "khmer_scam_full.csv")
    if not os.path.exists(path):
        path = os.path.join(RAW_DIR, "khmer_scam.csv")
    df = pd.read_csv(path)
    df["label"] = df["label"].map({"spam": 1, "ham": 0})
    col = "message" if "message" in df.columns else "text"
    df = df.rename(columns={col: "message"})
    return df[["message", "label"]]


def generate_synthetic_data():
    scam_templates = [
        "You won ${amount}! Click here to claim now",
        "URGENT: Your account will be suspended. Verify immediately",
        "Send your password to receive ${amount} reward",
        "Congratulations! You have been selected for a prize of ${amount}",
        "Your account has been compromised. Login now to secure it",
        "Free iPhone! Just send your credit card number",
        "You have inherited ${amount} from a distant relative",
        "Invest ${amount} and get ${multiplier} return in 24 hours",
        "FINAL NOTICE: Your power will be shut off today",
        "Hi Grandma, I'm in trouble. Please send ${amount} via Zelle",
        "Your Chase account has a suspicious charge of ${amount}",
        "Act now! Limited time offer to claim your ${amount} bonus",
        "Your account needs verification. Click here immediately",
        "You have won the lottery! Claim your ${amount} prize",
        "URGENT: Suspicious activity detected on your account",
        "Send money now or your account will be closed",
        "Invest now and earn ${amount} profit daily",
        "Your password expires today. Update immediately",
        "Congratulations! You won ${amount} in our sweepstakes",
        "Your account will be deleted. Verify now to keep it",
        "Someone accessed your account. Confirm your identity",
        "You have a pending reward of ${amount}. Claim now",
        "FINAL WARNING: Account suspended due to unusual activity",
        "Deposit ${amount} and receive ${multiplier} bonus",
        "Your payment of ${amount} is overdue. Pay now",
    ]

    safe_templates = [
        "Hey, how are you doing today?",
        "Can we meet for lunch tomorrow?",
        "Thanks for your help with the project",
        "Happy birthday! Hope you have a great day",
        "See you at the meeting at 3 PM",
        "I'll pick up the groceries on my way home",
        "The weather is nice today",
        "Did you watch the game last night?",
        "Let me know when you're available",
        "Sorry, I can't make it today",
        "Great job on the presentation!",
        "Can you send me the report?",
        "I'm running late, be there in 10 minutes",
        "Thanks for dinner, it was delicious",
        "Let's plan a trip this weekend",
        "I found that book you were looking for",
        "Call me when you get a chance",
        "The meeting has been rescheduled to 4 PM",
        "I hope you feel better soon",
        "Congratulations on your promotion!",
    ]

    import random
    amounts = ["100", "500", "1000", "5000", "10000", "100000", "1000000"]
    multipliers = ["2x", "3x", "5x", "10x", "100x"]

    data = []
    for _ in range(2000):
        template = random.choice(scam_templates)
        msg = template.replace("${amount}", random.choice(amounts))
        msg = msg.replace("${multiplier}", random.choice(multipliers))
        data.append({"message": msg, "label": 1})

    for _ in range(2000):
        template = random.choice(safe_templates)
        data.append({"message": template, "label": 0})

    return pd.DataFrame(data)


def train_text_model():
    logger.info("Loading datasets...")

    sms_df = load_sms_spam()
    logger.info(f"SMS Spam: {len(sms_df)} rows")

    khmer_df = load_khmer_scam()
    logger.info(f"Khmer: {len(khmer_df)} rows")

    synthetic_df = generate_synthetic_data()
    logger.info(f"Synthetic: {len(synthetic_df)} rows")

    all_df = pd.concat([sms_df, khmer_df, synthetic_df], ignore_index=True)
    all_df = all_df.dropna(subset=["message"])
    logger.info(f"Total: {len(all_df)} rows")

    X_train, X_test, y_train, y_test = train_test_split(
        all_df["message"], all_df["label"], test_size=0.2, random_state=42, stratify=all_df["label"]
    )

    logger.info("Training TF-IDF vectorizer...")
    tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        max_features=10000,
        sublinear_tf=True,
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    logger.info("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr.fit(X_train_tfidf, y_train)
    lr_acc = accuracy_score(y_test, lr.predict(X_test_tfidf))
    logger.info(f"LR accuracy: {lr_acc:.4f}")

    logger.info("Training Linear SVM...")
    svm = LinearSVC(max_iter=1000, random_state=42, C=1.0)
    svm.fit(X_train_tfidf, y_train)
    svm_acc = accuracy_score(y_test, svm.predict(X_test_tfidf))
    logger.info(f"SVM accuracy: {svm_acc:.4f}")

    print("\n" + "=" * 60)
    print("TEXT MODEL RESULTS")
    print("=" * 60)
    print(f"TF-IDF LR:  {lr_acc:.4f}")
    print(f"TF-IDF SVM: {svm_acc:.4f}")
    print("=" * 60)

    print("\nClassification Report (LR):")
    print(classification_report(y_test, lr.predict(X_test_tfidf), target_names=["safe", "scam"]))

    models = {
        "vectorizer": tfidf,
        "model": lr,
        "svm_model": svm,
    }

    out_path = os.path.join(PROC_DIR, "text_scam_model.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(models, f)
    logger.info(f"Model saved: {out_path}")

    test_texts = [
        "You won $1000000! Click here now",
        "Hey, how are you?",
        "សូមផ្ញើលុយមកខ្ញុំ",
        "URGENT: Your account will be suspended",
        "I love you baby",
        "Send your password to claim reward",
        "See you tomorrow at lunch",
        "Congratulations! You won the lottery",
    ]

    print("\nTest predictions:")
    for text in test_texts:
        X = tfidf.transform([text])
        pred = lr.predict(X)[0]
        label = "SCAM" if pred == 1 else "SAFE"
        print(f"  {text:45s} -> {label}")


if __name__ == "__main__":
    train_text_model()
