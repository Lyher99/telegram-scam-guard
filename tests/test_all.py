import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.features import analyze_message, extract_features
from bot.predict import predict_ensemble, predict_tfidf
from bot.report import format_report

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# ─── 1. Rule Baseline Tests ───────────────────────────────────
print("\n=== 1. Rule Baseline ===")

r = analyze_message("Hello friend, how are you?")
check("safe message", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = analyze_message("Urgent! Please help check this file invoice.pdf.exe immediately")
check("dangerous: double ext + urgency + help_check", r["risk_level"] == "dangerous", f"got {r['risk_level']}")

r = analyze_message("Click here to claim your prize money: https://bit.ly/fake")
check("suspicious: money_bait + link", r["risk_level"] in ("suspicious", "dangerous"), f"got {r['risk_level']}")

r = analyze_message("Send me your password and OTP")
check("dangerous: credential_ask", r["risk_level"] in ("suspicious", "dangerous"), f"got {r['risk_level']}")

r = analyze_message("Install this app now: malware.apk")
check("dangerous: install_ask + exec ext", r["risk_level"] == "dangerous", f"got {r['risk_level']}")

r = analyze_message("Great job opportunity! Salary $5000 work from home")
check("suspicious: job_bait", r["risk_level"] in ("suspicious", "dangerous"), f"got {r['risk_level']}")

r = analyze_message("Download this salary_report.xlsx")
check("suspicious: document ext + download", r["risk_level"] in ("suspicious", "safe"), f"got {r['risk_level']}")

# ─── 2. Feature Extraction Tests ──────────────────────────────
print("\n=== 2. Feature Extraction ===")

f = extract_features("Hello world")
check("no links", f["has_link"] == False)
check("no file", f["has_file"] == False)
check("no urgency", f["urgency"] == False)

f = extract_features("Check this https://evil.com https://another.com")
check("2 links detected", f["n_links"] == 2)

f = extract_features("Download invoice.pdf.exe now")
check("double ext detected", f["ext_exec"] == True)

f = extract_features("សូមពិនិត្យសារនេះ")
check("Khmer detected", f["has_khmer"] == True)

f = extract_features("Please open this file")
check("help_check_bait", f["help_check_bait"] == True)

# ─── 3. ML Model Tests ────────────────────────────────────────
print("\n=== 3. ML Model Predictions ===")

pred = predict_tfidf("https://www.google.com", "logistic_regression")
check("LR: google.com is safe", pred == "safe", f"got {pred}")

pred = predict_tfidf("http://45.135.193.63/arm7", "logistic_regression")
check("LR: IP malware URL is dangerous", pred == "dangerous", f"got {pred}")

pred = predict_tfidf("You have won $1,000,000 lottery! Claim now!", "logistic_regression")
check("LR: lottery scam", pred in ("suspicious", "dangerous"), f"got {pred}")

pred = predict_tfidf("invoice.pdf.exe", "logistic_regression")
check("LR: double ext file", pred == "dangerous", f"got {pred}")

pred = predict_tfidf("Meeting tomorrow at 3pm", "logistic_regression")
check("LR: normal message", pred == "safe", f"got {pred}")

pred = predict_tfidf("https://www.google.com", "linear_svm")
check("SVM: google.com is safe", pred == "safe", f"got {pred}")

pred = predict_tfidf("http://45.135.193.63/arm7", "linear_svm")
check("SVM: IP malware URL is dangerous", pred == "dangerous", f"got {pred}")

pred = predict_tfidf("invoice.pdf.exe", "linear_svm")
check("SVM: double ext file", pred == "dangerous", f"got {pred}")

# ─── 4. Ensemble Prediction Tests ─────────────────────────────
print("\n=== 4. Ensemble Predictions ===")

r = predict_ensemble("Hello, want to grab lunch?")
check("ensemble: safe message", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = predict_ensemble("Urgent! Help check this file document.pdf.exe now!")
check("ensemble: dangerous message", r["risk_level"] == "dangerous", f"got {r['risk_level']}")

r = predict_ensemble("http://45.135.193.63/malware.exe")
check("ensemble: malware URL", r["risk_level"] == "dangerous", f"got {r['risk_level']}")

r = predict_ensemble("Send me your OTP code please")
check("ensemble: OTP ask", r["risk_level"] in ("suspicious", "dangerous"), f"got {r['risk_level']}")

r = predict_ensemble("Check your email for the report")
check("ensemble: benign check", r["risk_level"] == "safe", f"got {r['risk_level']}")

# ─── 5. Report Format Tests ───────────────────────────────────
print("\n=== 5. Report Formatting ===")

r = predict_ensemble("Hello friend!")
report = format_report(r)
check("report has Safe", "Safe" in report)
check("report has Khmer", "មានសុវត្ថិភាព" in report)
check("report has Reasons", "Reasons" in report or "មូលហេតុ" in report)

r = predict_ensemble("Urgent! Help check invoice.pdf.exe!")
report = format_report(r)
check("report has Dangerous", "Dangerous" in report)
check("report has Khmer dangerous", "គ្រោះថ្នាក់" in report)

# ─── 6. Edge Cases ────────────────────────────────────────────
print("\n=== 6. Edge Cases ===")

r = analyze_message("")
check("empty string", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = analyze_message("a" * 10000)
check("long text", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = analyze_message("1234567890 !@#$%^&*()")
check("special chars only", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = predict_ensemble("https://www.southbankmosaics.com")
check("ensemble: known safe URL from PhiUSIIL", r["risk_level"] == "safe", f"got {r['risk_level']}")

# ─── 7. Money Lure Regression ─────────────────────────────────
print("\n=== 7. Money Lure ===")

r = predict_ensemble("ផ្ញើ $20 មក ខ្ញុំនឹងសង $200")
check("khmer send-small / get-big lure", r["risk_level"] == "dangerous", f"got {r['risk_level']}")

r = predict_ensemble("Send $50 now and get $500 back tomorrow")
check("english send/get ratio lure", r["risk_level"] in ("suspicious", "dangerous"), f"got {r['risk_level']}")

r = predict_ensemble("Please call me back when free")
check("benign 'when free' stays safe", r["risk_level"] == "safe", f"got {r['risk_level']}")

r = predict_ensemble("My salary is 1,500 USD per month")
check("salary statement stays safe", r["risk_level"] == "safe", f"got {r['risk_level']}")

# ─── Summary ──────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*50}")
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
print(f"{'='*50}")
