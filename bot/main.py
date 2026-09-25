import os
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from bot.report import format_report
from bot.predict import predict_ensemble
from bot.hash_lookup import check_hash

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_USERNAME = None


def is_group(update: Update) -> bool:
    return update.message.chat.type in ("group", "supergroup")


def should_respond(update: Update) -> bool:
    if not is_group(update):
        return True

    msg = update.message
    if msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.id == BOT_USERNAME:
        return True

    if msg.text and BOT_USERNAME and f"@{BOT_USERNAME}" in msg.text:
        return True

    if msg.document:
        return True

    if msg.text and ("http://" in msg.text or "www." in msg.text):
        return True

    if msg.text:
        suspicious_keywords = [
            "password", "verify", "account", "suspend", "urgent", "claim",
            "free", "won", "congrat", "credit card", "bank", "otp", "login",
            "confirm", "update", "security", "alert", "warning", "send money",
            "transfer", "crypto", "bitcoin", "wallet", "investment", "profit",
            "deposit", "receive", "million", "prize", "lottery", "selected",
            "inheritance", "winner", "bonus", "reward", "cash", "money",
            "salary", "job offer", "work from home", "earn", "income",
            "quick money", "easy money", "get rich", "financial freedom",
            "final notice", "shut off", "disconnection", "unpaid", "overdue",
            "suspended", "blocked", "closed", "unauthorized", "compromised",
            "grandma", "grandpa", "accident", "trouble", "hospital",
            "zelle", "venmo", "wire transfer", "send \$", "pay now",
            "fake", "scam", "phishing", "malware", "virus",
            "recover", "hacked", "hack", "gift card", "qr code",
            "six digits", "verification message", "follow my instructions",
            "deposit", "refundable", "investment opportunity", "guarantee",
            "forward it", "forward", "atm pin", "card details", "card number",
            "pin", "release fee", "delivery fee", "processing fee",
            "verification fee", "small payment", "small fee",
            "passport", "id card", "recruitment", "parcel", "delivery",
            "forward it", "forward", "confirm it",
            "scan this qr", "screenshot", "pay me first", "pay the seller",
            "reported", "before midnight", "cancel it", "cancelled",
            "recover your account", "recovery", "storage is full",
            "access their account", "cannot access", "friend asked",
            ".code", "send code", "send the code",
            "ផ្ញើលុយ", "ផ្ញើប្រាក់", "គណនី", "ធនាគារ", "ពាក្យសម្ងាត់",
        ]
        text_lower = msg.text.lower()
        if any(kw in text_lower for kw in suspicious_keywords):
            return True

    return False


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_group(update):
        await update.message.reply_text(
            "🔍 **Scam Guard** - ការពារក្រុមរបស់អ្នក\n\n"
            "📋 របៀបប្រើ:\n"
            "• ផ្ញើឯកសារ →  Bot ពិនិត្យឈ្មោះឯកសារ\n"
            "• ឆ្លើយតបទៅសារ + `/check` → Bot ពិនិត្យសារ\n"
            "• `/hash <sha256>` → ពិនិត្យ hash ឯកសារ\n\n"
            "⚠️ Bot មិនទាញយកឯកសារទេ - ពិនិត្យតែ metadata ប៉ុណ្ណោះ។",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🔍 **Telegram Scam Guard**\n\n"
            "📋 របៀបប្រើ:\n"
            "• ផ្ញើសារសង្ស័យ → Bot ពិនិត្យ\n"
            "• ផ្ញើឯកសារ → Bot ពិនិត្យឈ្មោះ\n"
            "• `/hash <sha256>` → ពិនិត្យ hash\n\n"
            "⚠️ Bot មិនទាញយកឯកសារទេ - ពិនិត្យតែ metadata ប៉ុណ្ណោះ។",
            parse_mode="Markdown"
        )


async def cmd_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔍 **ពិនិត្យឯកសារ**\n\n"
            "ប្រើ: /hash <sha256>\n\n"
            "ឧទាហរណ៍:\n"
            "`/hash 44d88612fea8a8f36de82e1278abb02f...`\n\n"
            "💡 រក SHA256 បានពី:\n"
            "• VirusTotal.com\n"
            "• HashMyFiles (NirSoft)\n"
            "• PowerShell: `Get-FileHash file.bat`",
            parse_mode="Markdown"
        )
        return

    sha256 = args[0].strip()
    if len(sha256) != 64:
        await update.message.reply_text(
            "❌ Hash ត្រូវតែ 64 អក្សរ (SHA256)\n\n"
            "ប្រើ: /hash <sha256_hash>"
        )
        return

    waiting_msg = await update.message.reply_text("🔍 កំពុងពិនិត្យ...")

    result = await check_hash(sha256)

    if result.get("error"):
        await waiting_msg.edit_text(f"❌ មានបញ្ហា: {result['error']}")
        return

    if result.get("found"):
        tags = ", ".join(result.get("tags", [])) if result.get("tags") else ""
        report = (
            f"🚨 **រកឃើញមេរោគ!**\n\n"
            f"📄 ប្រភេទ: {result.get('file_type', 'unknown')}\n"
            f"📝 ឈ្មោះ: {result.get('file_name', 'unknown')}\n"
            f"🔍 ហត្ថលេខា: {result.get('signature', 'unknown')}\n"
            f"📅 ឃើញដំបូង: {result.get('first_seen', 'unknown')}"
        )
        if tags:
            report += f"\n🏷️ Tags: {tags}"
    else:
        report = (
            "✅ **រកមិនឃើញមេរោគ**\n\n"
            "⚠️ ប៉ុន្តែនេះមិនមែនមានន័យថា\n"
            "ឯកសារមានសុវត្ថិភាព 100% ទេ។\n\n"
            "💡 សូមប្រុងប្រយ័ត្ននៅតែដដែល។"
        )

    await waiting_msg.edit_text(report, parse_mode="Markdown")


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message with /check to scan it.")
        return

    target = update.message.reply_to_message
    text = target.text or target.caption or ""
    if target.document:
        file_name = target.document.file_name or "unknown"
        file_size_kb = round(target.document.file_size / 1024, 1) if target.document.file_size else 0
        mime = target.document.mime_type or "unknown"
        text = f"{file_name} (size: {file_size_kb}KB, type: {mime})"

    if not text:
        await update.message.reply_text("No text or file to scan.")
        return

    result = predict_ensemble(text)
    report = format_report(result)
    await update.message.reply_text(report)


import re


def extract_urls(text):
    url_pattern = re.compile(r'https?://[^\s<>\"\')]+|www\.[^\s<>\"\')]+')
    return url_pattern.findall(text)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    if is_group(update) and not should_respond(update):
        return

    clean_text = text
    if BOT_USERNAME:
        clean_text = clean_text.replace(f"@{BOT_USERNAME}", "").strip()

    urls = extract_urls(clean_text)

    if urls:
        from bot.url_predict import predict_url

        url_dangerous = False
        for url in urls[:3]:
            url_result = predict_url(url)

            if url_result.get("ensemble") == 1:
                prob = url_result.get("avg_prob", 0) * 100
                report = f"🚫 **Link គ្រោះថ្នាក់!**\n\n"
                report += f"🔗 `{url[:60]}...`\n"
                report += f"• ឱកាសជា phishing: {prob:.0f}%\n\n"
                report += f"💡 **កុំចុច Link នេះ!**"
                await update.message.reply_text(report, parse_mode="Markdown")
                url_dangerous = True

        text_result = predict_ensemble(clean_text)
        if text_result["risk_level"] != "safe":
            report = format_report(text_result)
            await update.message.reply_text(report)
        elif not url_dangerous:
            await update.message.reply_text(
                f"✅ **Link មានសុវត្ថិភាព**\n\n🔗 `{urls[0][:60]}`",
                parse_mode="Markdown"
            )
        return

    result = predict_ensemble(clean_text)
    ml = result.get("ml_predictions", {})

    report = format_report(result)

    ml_info = "\n\n🤖 **ការវិភាគ ML:**\n"
    ml_info += f"• Rule: {ml.get('rule', '-')}\n"
    ml_info += f"• Text LR: {ml.get('text_lr', '-')}\n"
    ml_info += f"• Text SVM: {ml.get('text_svm', '-')}"

    await update.message.reply_text(report + ml_info, parse_mode="Markdown")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return

    file_name = doc.file_name or "unknown"
    file_size_kb = round(doc.file_size / 1024, 1) if doc.file_size else 0
    mime = doc.mime_type or "unknown"
    ext = os.path.splitext(file_name)[1].lower()

    DANGEROUS_EXTS = {".exe", ".scr", ".bat", ".cmd", ".com", ".msi", ".js", ".vbs", ".jar", ".apk", ".lnk", ".ps1", ".hta", ".pif", ".dll", ".reg", ".sh"}
    ZIP_EXTS = {".zip", ".rar", ".7z"}
    SAFE_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".txt", ".mp4", ".mp3", ".csv", ".rtf"}

    if ext in SAFE_EXTS:
        return

    if ext in DANGEROUS_EXTS:
        if doc.file_size and doc.file_size <= 20 * 1024 * 1024:
            try:
                waiting_msg = await update.message.reply_text("🔍 កំពុងពិនិត្យឯកសារ...")
                tg_file = await context.bot.get_file(doc.file_id)
                file_bytes = await tg_file.download_as_bytearray()

                from bot.deep_check import deep_check_file
                deep = deep_check_file(bytes(file_bytes), ext)

                from bot.hash_lookup import check_hash
                hash_result = await check_hash(deep["sha256"])

                report = f"🚫 **គ្រោះថ្នាក់ ({file_size_kb}KB)**\n\n"
                report += f"📄 `{file_name}`\n"
                report += f"• ប្រភេទពិត: {deep['real_type']}\n"

                if hash_result.get("found"):
                    report += f"🚨 **រកឃើញមេរោគ!** {hash_result.get('signature', '')}\n"

                report += f"\n💡 **កុំដំណើរការឯកសារនេះ!**"
                report += f"\n🔗 ពិនិត្យបន្ថែម: https://www.virustotal.com"
                await waiting_msg.edit_text(report, parse_mode="Markdown")
                return
            except Exception as e:
                logger.error(f"Deep check error: {e}")

        result = predict_ensemble(f"{file_name} (size: {file_size_kb}KB, type: {mime})")
        report = format_report(result)
        report += f"\n🔗 ពិនិត្យបន្ថែម: https://www.virustotal.com"
        await update.message.reply_text(report)
        return

    if ext in ZIP_EXTS:
        if doc.file_size and doc.file_size <= 50 * 1024 * 1024:
            try:
                waiting_msg = await update.message.reply_text("🔍 កំពុងពិនិត្យមាតិកា ZIP...")
                tg_file = await context.bot.get_file(doc.file_id)
                file_bytes = await tg_file.download_as_bytearray()

                from bot.zip_check import check_zip_contents
                zip_result = check_zip_contents(bytes(file_bytes))

                if zip_result["dangerous_files"]:
                    dangerous_list = "\n".join(f"• `{f}`" for f in zip_result["dangerous_files"][:10])
                    report = f"🚫 **គ្រោះថ្នាក់! ZIP មាន Program ខុស!**\n\n"
                    report += f"📄 `{file_name}` ({zip_result['total_files']} files)\n\n"
                    report += f"🚨 **ឯកសារគ្រោះថ្នាក់ក្នុង ZIP:**\n{dangerous_list}\n\n"
                    report += f"💡 **កុំដំឡើងឯកសារទាំងនេះ!**"
                    await waiting_msg.edit_text(report, parse_mode="Markdown")
                    return

                if zip_result["has_double_ext"]:
                    report = f"⚠️ **គួរឱ្យសង្ស័យ**\n\n"
                    report += f"📄 `{file_name}`\n"
                    report += f"• មានឯកសារ double extension ក្នុង ZIP\n\n"
                    report += f"💡 **ប្រុងប្រយ័ត្ន!**"
                    await waiting_msg.edit_text(report, parse_mode="Markdown")
                    return

                await waiting_msg.delete()
                return
                return

            except Exception as e:
                logger.error(f"ZIP check error: {e}")

        result = predict_ensemble(f"{file_name} (size: {file_size_kb}KB, type: {mime})")
        report = format_report(result)
        report += f"\n🔗 ពិនិត្យបន្ថែម: https://www.virustotal.com"
        await update.message.reply_text(report)
        return

    result = predict_ensemble(f"{file_name} (size: {file_size_kb}KB, type: {mime})")
    report = format_report(result)
    report += f"\n🔗 ពិនិត្យបន្ថែម: https://www.virustotal.com"
    await update.message.reply_text(report)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I cannot scan images. Please describe the message text or send the file name instead.\n\n"
        "ខ្ញុំមិនអាចពិនិត្យរូបភាពបានទេ។ សូមបរិយាយអត្ថបទសារ ឬផ្ញើឈ្មោះឯកសារជំនួសវិញ។"
    )


def main():
    global BOT_USERNAME

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        raise SystemExit("Set TELEGRAM_BOT_TOKEN environment variable")

    app = ApplicationBuilder().token(token).build()

    import asyncio
    async def post_init(application):
        global BOT_USERNAME
        me = await application.bot.get_me()
        BOT_USERNAME = me.username
        logger.info(f"Bot username: @{BOT_USERNAME}")

    app.post_init = post_init

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("check", cmd_check))
    app.add_handler(CommandHandler("hash", cmd_hash))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
