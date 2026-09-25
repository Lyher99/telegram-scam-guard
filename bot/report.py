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
    score = result["score"]
    reasons = result["reasons"]

    labels = RISK_LABELS[risk]
    icon = labels["icon"]

    translated_reasons = []
    for r in reasons:
        if r in REASON_TRANSLATIONS:
            translated_reasons.append(REASON_TRANSLATIONS[r]["km"])
        else:
            translated_reasons.append(f"• {r}")

    reason_text = "\n".join(translated_reasons) if translated_reasons else "• មិនរកឃើញហានិភ័យច្បាស់លាស់"

    if risk == "safe":
        header = f"{icon} **មានសុវត្ថិភាព**"
        advice = (
            "✅ សារនេះមានលក្ខណៈធម្មតា។\n"
            "ប៉ុន្តែសូមប្រុងប្រយ័ត្នជានិច្ចចំពោះតំណភ្ជាប់ និងឯកសារពីអ្នកដែលអ្នកមិនស្គាល់។"
        )
    elif risk == "suspicious":
        header = f"{icon} **គួរឱ្យសង្ស័យ ({score}%)**"
        advice = (
            "⚠️ សារនេះគួរឱ្យសង្ស័យ!\n"
            "កុំចុចតំណភ្ជាប់ ឬបើកឯកសារ។\n"
            "សូមផ្ទៀងផ្ទាត់ជាមួយអ្នកផ្ញើតាមប្រព័ន្ធផ្សេង។"
        )
    else:
        header = f"{icon} **គ្រោះថ្នាក់ ({score}%)**"
        advice = (
            "🚫 សារនេះគ្រោះថ្នាក់!\n"
            "កុំបើកឯកសារ ឬចុចតំណភ្ជាប់!\n"
            "សូមសួរអ្នកផ្ញើតាមប្រព័ន្ធផ្សេង។"
        )

    report = f"""{header}

{reason_text}

💡 **អនុសាសន៍:**
{advice}"""

    return report
