"""
Bilingual Report Formatter
===========================
Flow & Responsibilities:
1. Translates internal detection categories and reasons into human-friendly explanations.
2. Generates dual-language output (Khmer + English) formatted for Telegram Markdown.
3. Provides contextual action recommendations (e.g., "Do not open this file", "Ask the sender via another channel").
"""

import re

RISK_LABELS = {
    "safe": {"en": "Safe", "km": "មានសុវត្ថិភាព", "icon": "✅"},
    "suspicious": {"en": "Suspicious", "km": "គួរឱ្យសង្ស័យ", "icon": "⚠️"},
    "dangerous": {"en": "Dangerous", "km": "គ្រោះថ្នាក់", "icon": "🚫"},
}

REASON_TRANSLATIONS = {
    "File has an executable extension (.exe/.bat/.scr/.apk)": {
        "en": "⚠️ File is an executable program (.exe/.bat/.scr/.apk)",
        "km": "⚠️ ឯកសារជា Program ដែលអាចដំណើរការបាន (.exe/.bat/.scr/.apk)",
    },
    "Double extension detected (fake document)": {
        "en": "🔴 Fake file name - pretends to be a document",
        "km": "🔴 ឈ្មោះឯកសារក្លែងក្លាយ - ធ្វើជាឯកសារ",
    },
    "Message uses urgency language": {
        "en": "⏰ Uses pressure words (urgent, immediately)",
        "km": "⏰ ប្រើពាក្យដាក់សម្ពាធ (បន្ទាន់, ភ្លាមៗ)",
    },
    "Message asks you to check/open something": {
        "en": "📩 Asks you to check or open something",
        "km": "📩 សូមឱ្យអ្នកពិនិត្យ ឬបើកអ្វីមួយ",
    },
    "Money or prize bait detected": {
        "en": "💰 Mentions money, prize, or lottery",
        "km": "💰 និយាយពីលុយ, រង្វាន់, ឬឆ្នោត",
    },
    "Money amount lure (send small amount, promised much larger return)": {
        "en": "💸 Asks you to send a small amount, promises a much bigger return",
        "km": "💸 សុំផ្ញើលុយតិច ប៉ុន្តែសន្យាថានឹងសងវិញច្រើនដង",
    },
    "Money lure combined with bait wording": {
        "en": "💸 Money lure combined with bait wording (free/prize/invest)",
        "km": "💸 ល្បួងលុយរួមជាមួយពាក្យល្បួង (ឥតគិតថ្លៃ/រង្វាន់/វិនិយោគ)",
    },
    "Money amount lure detected (send small, promised much larger return)": {
        "en": "💸 Send a small amount, promised much larger return",
        "km": "💸 ផ្ញើលុយតិច ប៉ុន្តែសន្យាថានឹងសងវិញច្រើនដង",
    },
    "Job offer bait detected": {
        "en": "💼 Job offer or salary promise",
        "km": "💼 ផ្តល់ការងារ ឬប្រាក់ខែ",
    },
    "Asks for login credentials or OTP": {
        "en": "🔑 Asks for password, OTP, or login info",
        "km": "🔑 សូមពាក្យសម្ងាត់, OTP, ឬព័ត៌មានចូល",
    },
    "Asks you to install or run something": {
        "en": "📲 Asks you to install or download something",
        "km": "📲 សូមឱ្យអ្នកដំឡើង ឬទាញយកអ្វីមួយ",
    },
    "Archive file detected (.zip/.rar/.7z) - contents hidden": {
        "en": "📦 Archive file - contents cannot be checked",
        "km": "📦 ឯកសារបញ្ចប់ (zip/rar/7z) - មិនអាចពិនិត្យខ្លឹមសារបាន",
    },
    "Archive has a lure name (invoice/salary/document)": {
        "en": "🎭 Archive name looks like a lure (invoice/salary/document)",
        "km": "🎭 ឈ្មោះឯកសារដូចជាការល្បួង (វិក័យប័ត្រ/ប្រាក់ខែ/ឯកសារ)",
    },
    "Password-protected archive mentioned": {
        "en": "🔐 Password-protected archive (common in scams)",
        "km": "🔐 ឯកសារការពារដោយពាក្យសម្ងាត់ (ញឹកញាប់ក្នុងការក្លែងបន្លំ)",
    },
    "Link combined with executable file": {
        "en": "🔗 Link + executable file together",
        "km": "🔗 តំណភ្ជាប់ + ឯកសារអាចដំណើរការបាន",
    },
    "Link combined with archive file": {
        "en": "🔗 Link + archive file together",
        "km": "🔗 តំណភ្ជាប់ + ឯកសារបញ្ចប់",
    },
}


def format_report(result):
    risk = result["risk_level"]
    reasons = result["reasons"]

    labels = RISK_LABELS[risk]
    icon = labels["icon"]

    translated_reasons = []
    for r in reasons:
        if r.startswith("ML model detected scam"):
            translated_reasons.append("សារមានពាក្យសង្ស័យ / Suspicious wording")
        elif r in REASON_TRANSLATIONS:
            english_reason = re.sub(r"^[^A-Za-z]+", "", REASON_TRANSLATIONS[r]["en"])
            translated_reasons.append(
                f"{REASON_TRANSLATIONS[r]['km']} / {english_reason}"
            )
        else:
            translated_reasons.append("សារមានសញ្ញាគួរឱ្យសង្ស័យ / Message looks suspicious")

    # Keep the reply brief and avoid repeating the same reason in different wording.
    unique_reasons = list(dict.fromkeys(translated_reasons))[:2]
    reason_text = "\n".join(f"• {reason}" for reason in unique_reasons)

    if risk == "safe":
        header = f"{icon} **ហានិភ័យទាប / Safe**"
        advice = "កុំចុចតំណភ្ជាប់ ឬបើកឯកសារដែលអ្នកមិនស្គាល់។ / Avoid unknown links and files."
    elif risk == "suspicious":
        header = f"{icon} **គួរឱ្យសង្ស័យ / Suspicious**"
        advice = "កុំចុចតំណ ឬផ្ញើលេខកូដ។ ផ្ទៀងផ្ទាត់ជាមួយអ្នកផ្ញើ។ / Don’t click or share codes. Verify with the sender."
    else:
        header = f"{icon} **គ្រោះថ្នាក់ / Dangerous**"
        advice = "កុំចុចតំណ ឬបើកឯកសារ។ ផ្ទៀងផ្ទាត់ជាមួយអ្នកផ្ញើ។ / Don’t click or open files. Verify with the sender."

    report = f"{header}"
    if reason_text:
        report += f"\n{reason_text}"
    report += f"\n\n{advice}"

    return report
