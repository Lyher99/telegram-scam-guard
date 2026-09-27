# Contributing to Telegram Scam Guard

Thank you for your interest in improving Telegram Scam Guard!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lyher99/telegram-scam-guard.git
   cd telegram-scam-guard
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Add your Telegram bot token to .env
   ```

## Running Tests

Before submitting a Pull Request, please ensure all tests pass:

```bash
python tests/test_all.py
pytest
```

## Dataset Contributions

- To contribute new Khmer or English scam patterns or keyword lures, update [`src/features.py`](file:///home/ubuntu/code/Telegram/src/features.py).
- For privacy reasons, ensure all personal names, phone numbers, account numbers, and credentials are anonymized before contributing dataset samples.
