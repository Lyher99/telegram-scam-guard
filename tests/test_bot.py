from bot.report import format_report
from src.features import analyze_message


def test_format_report_safe():
    result = analyze_message("Hello, how are you?")
    report = format_report(result)
    assert "Safe" in report
    assert "មានសុវត្ថិភាព" in report


def test_format_report_suspicious():
    result = analyze_message("Please check this link https://evil.com and send your OTP")
    report = format_report(result)
    assert "Suspicious" in report or "Dangerous" in report


def test_format_report_dangerous():
    result = analyze_message("Urgent! Please help check this file invoice.pdf.exe immediately")
    report = format_report(result)
    assert "Dangerous" in report
    assert "គ្រោះថ្នាក់" in report


def test_format_report_has_reasons():
    result = analyze_message("Urgent! Open this file now test.exe")
    report = format_report(result)
    assert "Reasons" in report or "មូលហេតុ" in report
