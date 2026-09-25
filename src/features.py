import re

EXECUTABLE_EXTS = {"exe", "scr", "bat", "cmd", "com", "msi", "js", "vbs", "jar", "apk", "lnk", "ps1", "hta", "pif", "dll", "reg", "sh"}
DOCUMENT_EXTS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "jpg", "jpeg", "png", "gif", "txt", "mp4", "mp3", "csv", "rtf"}
ARCHIVE_EXTS = {"zip", "rar", "7z", "iso", "img", "tar", "gz"}

LURE_NAMES_EN = ["invoice", "salary", "payment", "document", "important", "urgent", "confidential", "receipt", "tax", "report", "resume"]
LURE_NAMES_KM = ["វិក័យប័ត្រ", "ប្រាក់ខែ", "ឯកសារ"]
PASSWORD_ASK_EN = ["password", "pw", "pass:", "pw:", "password:", "the password is", "password is"]
PASSWORD_ASK_KM = ["ពាក្យសម្ងាត់", "កូដេង", "ពាក្យសំងាត់", "លេខសម្ងាត់"]

URGENCY_EN = ["urgent", "immediately", "asap", "hurry", "quick", "now", "right away", "don't wait", "final notice", "last warning", "shut off", "disconnection", "suspended", "blocked", "closed", "unauthorized", "act now", "before it's too late", "deadline", "expire", "limited time", "before midnight", "reported", "will be cancelled", "within 10 minutes", "within 15 minutes", "has been", "has a", "is a", "there is", "there has"]
URGENCY_KM = ["បន្ទាន់", "ភ្លាមៗ", "ឥឡូវនេះ", "រួសរាន់", "កំណត់ពេល", "ផុតកំណត់", "ចុងក្រោយ", "ព្រមាន", "នឹងត្រូវបិទ", "នឹងត្រូវផ្អាក"]
MONEY_BAIT_EN = ["money", "cash", "prize", "winner", "lottery", "inheritance", "transfer", "bank", "won", "free", "iphone", "claim", "reward", "bonus", "gift", "congratulations", "congrats", "selected", "chosen", "deposit", "invest", "profit", "return", "million", "thousand", "rich", "wealth", "fortune", "lucky", "jackpot", "guarantee", "refundable", "recovered", "hacked", "compromised", "double", "triple", "multiply", "10x", "20x", "100x", "48 hours", "24 hours", "within 2 days", "two days", "three days", "2 days", "3 days", "i promise", "i guarantee", "guaranteed return", "risk free", "zero risk", "no risk", "safe investment", "quick money", "fast money", "easy money", "no experience", "just send", "pay first", "send first", "give me", "send me", "trust me", "put in", "withdraw", "gain", "earn", "make money", "become rich", "financial freedom", "get rich", "daily income", "weekly income", "high return", "passive income", "investment opportunity", "turn your money", "make it", "back tomorrow", "receive tomorrow", "return tomorrow", "receive today", "become", " francs", "riel", "dollars", "send $", "pay $", "give $", "invest $", "deposit $", "send 20", "send 50", "send 100", "give 20", "give 50", "give 100", "pay 20", "pay 50", "pay 100", "double your", "ten times", "turn your", "become", "into", "out after", "back in", "start with", "only need", "small investment", "guaranteed profit", "guaranteed return", "no experience needed"]
MONEY_BAIT_KM = ["លុយ", "ប្រាក់", "ឈ្នះ", "ឆ្នោត", "ឥតគិតថ្លៃ", "ជ័យជំនះ", "រង្វាន់", "ប្រាក់រង្វាន់", "ដាក់ប្រាក់", "វិនិយោគ", "ចំណេញ", "ទទួលបាន", "សម្បត្តិ", "សំណាង", "បង្វិល", "ធានា", "បង្កើន", "កើន", "សង", "យក", "ទទួល", "ចូល", "ចេញ", "មួយដង", "ដង"]
JOB_BAIT_EN = ["job", "salary", "hiring", "work from home", "earn", "income", "opportunity", "make money", "easy money", "quick money"]
JOB_BAIT_KM = ["ការងារ", "ប្រាក់ខែ", "ឱការការងារ", "រកស៊ី", "ចំណូល"]
HELP_CHECK_EN = ["help check", "please check", "look at this", "open this", "review this"]
HELP_CHECK_KM = ["ជួយពិនិត្យ", "សូមពិនិត្យ"]
CREDENTIAL_ASK = ["password", "login", "username", "otp", "verify your account", "confirm your", "send password", "enter password", "bank account", "credit card", "card number", "គណនី", "ពាក្យសម្ងាត់", "លេខកូដ", "ធនាគារ", "send money", "zelle", "venmo", "cashapp", "wire transfer", "gift card", "qr code", "six digits", "verification code", "follow my instructions", "send me the", "return it", "send it back", "atm pin", "card details", "pin", "release fee", "delivery fee", "processing fee", "verification fee", "small payment", "small fee", "passport", "id card", "recruitment", "parcel", "delivery", "forward it", "forward", "confirm it", "scan this qr", "screenshot", "pay me first", "pay the seller", "recovery codes", "backup codes", "2fa", "security code", "confirmation code", "account owner", "verify ownership", "blocked tonight", "private", "keep this private", "code you receive", "receive by sms", "code from your phone", "high-paying job"]
INSTALL_ASK = ["install", "download", "run this", "open the file", "enable"]

PAYMENT_SCAM_EN = ["payment failed", "new payment link", "cancel it", "cancelled", "unpaid", "penalty",
                   "cannot access", "friend asked", "code you receive", "receive by sms",
                   "pay to unlock", "pay to activate", "pay to release", "pay to confirm",
                   "verification payment", "small payment", "release fee", "processing fee"]

FAMILY_SCAM_EN = ["grandma", "grandpa", "grandmother", "grandfather", "accident", "trouble", "hospital", "arrested", "jail", "emergency", "help me", "don't tell", "don't call", "send money", "wire money"]
FAMILY_SCAM_KM = ["ជួយខ្ញុំ", "គ្រោះថ្នាក់", "មន្ទីរពេទ្យ", "ឃុំឃាំង", "កុំប្រាប់", "កុំទូរស័ព្ទ"]


def _has_keyword(text, keywords):
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _extract_urls(text):
    return re.findall(r'https?://[^\s<>\"\']+', text)


def _extract_file_info(text):
    match = re.search(r'(\S+\.(exe|scr|bat|cmd|com|msi|js|vbs|jar|apk|lnk|ps1|hta|pif|dll|reg|sh|pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z))', text, re.IGNORECASE)
    if match:
        name = match.group(1)
        ext = match.group(2).lower()
        return name, ext
    return None, None


def extract_features(text):
    urls = _extract_urls(text)
    file_name, file_ext = _extract_file_info(text)

    features = {
        "text_len": len(text),
        "has_khmer": bool(re.search(r'[\u1780-\u17FF]', text)),
        "urgency": _has_keyword(text, URGENCY_EN + URGENCY_KM),
        "money_bait": _has_keyword(text, MONEY_BAIT_EN + MONEY_BAIT_KM),
        "job_bait": _has_keyword(text, JOB_BAIT_EN + JOB_BAIT_KM),
        "help_check_bait": _has_keyword(text, HELP_CHECK_EN + HELP_CHECK_KM),
        "credential_ask": _has_keyword(text, CREDENTIAL_ASK),
        "install_ask": _has_keyword(text, INSTALL_ASK),
        "payment_scam": _has_keyword(text, PAYMENT_SCAM_EN),
        "family_scam": _has_keyword(text, FAMILY_SCAM_EN + FAMILY_SCAM_KM),
        "has_link": len(urls) > 0,
        "n_links": len(urls),
        "has_file": file_name is not None,
        "file_name": file_name,
        "ext_exec": file_ext in EXECUTABLE_EXTS if file_ext else False,
        "ext_archive": file_ext in ARCHIVE_EXTS if file_ext else False,
        "archive_lure_name": False,
        "password_archive": False,
    }

    if file_name and file_ext in ARCHIVE_EXTS:
        name_lower = file_name.lower()
        features["archive_lure_name"] = any(ln in name_lower for ln in LURE_NAMES_EN + LURE_NAMES_KM)
        features["password_archive"] = _has_keyword(text, PASSWORD_ASK_EN + PASSWORD_ASK_KM)

    return features


def rule_baseline(features):
    reasons = []
    score = 0

    if features["ext_exec"]:
        reasons.append("File has an executable extension (.exe/.bat/.scr/.apk)")
        score += 60
        if features["file_name"] and "." in features["file_name"]:
            parts = features["file_name"].rsplit(".", 2)
            if len(parts) >= 3:
                reasons.append("Double extension detected (fake document)")
                score += 25

    if features["urgency"]:
        reasons.append("Message uses urgency language")
        score += 15

    if features["help_check_bait"]:
        reasons.append("Message asks you to check/open something")
        score += 20

    if features["money_bait"]:
        reasons.append("Money or prize bait detected")
        score += 15

    if features["job_bait"]:
        reasons.append("Job offer bait detected")
        score += 15

    if features["credential_ask"]:
        reasons.append("Asks for login credentials or OTP")
        score += 25

    if features["install_ask"]:
        reasons.append("Asks you to install or run something")
        score += 15

    if features.get("payment_scam"):
        reasons.append("Payment scam pattern detected")
        score += 20

    if features.get("family_scam"):
        reasons.append("Family emergency scam pattern detected")
        score += 20

    if features["has_link"]:
        score += 5

    if features["has_link"] and features["ext_exec"]:
        reasons.append("Link combined with executable file")
        score += 10

    if features["ext_archive"]:
        has_other_risk = any([
            features["urgency"], features["money_bait"], features["job_bait"],
            features["help_check_bait"], features["credential_ask"],
            features["install_ask"], features["has_link"],
        ])

        if features["password_archive"]:
            reasons.append("Password-protected archive")
            score += 30
        elif features["archive_lure_name"] and has_other_risk:
            reasons.append("Archive with lure name + suspicious message")
            score += 25
        elif features["ext_exec"] and features["ext_archive"]:
            reasons.append("Archive with executable extension")
            score += 20

    if len(reasons) >= 3:
        score += 10

    if len(reasons) >= 2 and score < 50:
        score += 5

    score = min(score, 100)

    if score >= 50:
        risk_level = "dangerous"
    elif score >= 15:
        risk_level = "suspicious"
    else:
        risk_level = "safe"

    return {"risk_level": risk_level, "score": score, "reasons": reasons}


def analyze_message(text):
    features = extract_features(text)
    return rule_baseline(features)
