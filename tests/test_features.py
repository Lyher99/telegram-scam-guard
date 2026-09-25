from src.features import analyze_message


def test_analyze_message_returns_dict():
    result = analyze_message("Hello, how are you?")
    assert isinstance(result, dict)
    assert "risk_level" in result
    assert "reasons" in result


def test_safe_message():
    result = analyze_message("Hey, want to grab lunch tomorrow?")
    assert result["risk_level"] == "safe"


def test_suspicious_message():
    result = analyze_message("Send me your bank details and OTP code please")
    assert result["risk_level"] in ("suspicious", "dangerous")


def test_dangerous_message():
    result = analyze_message("Urgent! Please help check this file invoice.pdf.exe immediately")
    assert result["risk_level"] == "dangerous"
