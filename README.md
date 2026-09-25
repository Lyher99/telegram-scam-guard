# Telegram Scam Guard (Khmer + English)

A Telegram bot that detects phishing/scam messages, malicious URLs, and suspicious files in **Khmer** and **English** using a hybrid keyword + machine learning approach trained on public datasets.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [How It Works](#2-how-it-works)
3. [Architecture](#3-architecture)
4. [Machine Learning Models](#4-machine-learning-models)
5. [Datasets](#5-datasets)
6. [Feature Engineering](#6-feature-engineering)
7. [Bot Capabilities](#7-bot-capabilities)
8. [Detection Pipeline](#8-detection-pipeline)
9. [Setup & Deployment](#9-setup--deployment)
10. [Testing Results](#10-testing-results)
11. [Project Structure](#11-project-structure)
12. [Limitations](#12-limitations)

---

## 1. Project Overview

**Problem:** In Cambodian Telegram communities, users receive scam links, fake files (e.g. `invoice.pdf.exe`), and pressure messages. Installing or running these files can take over accounts.

**Goal:** A Telegram bot that takes a message, link, or file *metadata* and returns a risk level with human-readable reasons in Khmer and English.

**Safety Rule:** The bot **never** downloads, opens, or executes any file. It only inspects metadata (file name, extension, size, magic bytes).

---

## 2. How It Works

The detection system uses a **hybrid approach** combining three layers:

```
Input Message
    │
    ├── Text Analysis ──→ Keyword Features (11 binary) + TF-IDF (10,000 words)
    │                         │
    │                    Logistic Regression + Linear SVM
    │                         │
    │                    ML Score (0-100%)
    │
    ├── URL Analysis ──→ 28 URL Features → LR + SVM → Phishing Score
    │
    ├── File Check ──→ Magic Bytes + Extension Mismatch → Risk Type
    │
    └── Hash Lookup ──→ Local MalwareBazaar DB (1,762 hashes)
    │
    └── ZIP Check ──→ Archive Contents Inspection (.exe inside?)
    │
    ▼
Final Decision: safe / suspicious / dangerous
```

### Scoring Logic

| Component | Weight | Details |
|-----------|--------|---------|
| Keyword match | 25 points each | Each matched keyword category adds 25 points |
| ML prediction | 70-100% | Only used if confidence ≥ 70% (to avoid false positives) |
| Combined | max(kw_score, ml_score) | Keywords boost ML; ML alone needs ≥ 70% confidence |

| Final Score | Risk Level |
|-------------|------------|
| ≥ 60% | 🚫 Dangerous |
| ≥ 25% | ⚠️ Suspicious |
| < 25% | ✅ Safe |

---

## 3. Architecture

```
Telegram Bot (python-telegram-bot)
    │
    ├── bot/main.py          ← Entry point, message handlers
    ├── bot/predict.py       ← Hybrid text prediction engine
    ├── bot/url_predict.py   ← URL phishing detection
    ├── bot/url_features.py  ← 28 URL feature extraction
    ├── bot/report.py        ← Khmer/English report formatting
    ├── bot/deep_check.py    ← Magic bytes + extension mismatch
    ├── bot/zip_check.py     ← ZIP contents inspection
    └── bot/hash_lookup.py   ← Local SHA256 hash lookup
    │
    ├── src/features.py      ← Keyword lists + feature extraction
    └── src/train_hybrid.py  ← Model training script
    │
    └── data/
        ├── raw/             ← Datasets (CSV)
        └── processed/       ← Trained models (PKL)
```

**Runs outside Docker** (Docker cannot reach Telegram API). Managed via `screen` sessions.

---

## 4. Machine Learning Models

### 4.1 Text Model (Hybrid)

**Type:** Logistic Regression + Linear SVM ensemble on TF-IDF + keyword features.

| Component | Details |
|-----------|---------|
| TF-IDF | 10,000 max features, unigrams + bigrams, sublinear TF |
| Keyword features | 11 binary indicators (urgency, money bait, credential ask, etc.) |
| Combined input | Sparse hstack of TF-IDF + keyword features |
| LR accuracy | **94.6%** |
| SVM accuracy | **95.4%** |
| Training data | 52,405 messages (18,561 spam + 33,844 ham) |

**Why hybrid?** Pure TF-IDF misses short Khmer messages with few words. Keyword features catch patterns like "ផ្ញើ $20 មក ខ្ញុំនឹងសង $200" even when the ML model has low confidence.

### 4.2 URL Model

**Type:** Feature-based LR + SVM on 28 hand-crafted URL features.

| Component | Details |
|-----------|---------|
| Features | 28 (URL length, domain depth, suspicious TLDs, entropy, etc.) |
| Safe domain whitelist | 40+ known safe domains (google.com, facebook.com, etc.) |
| Accuracy | **96.9%** |
| Training data | 235,795 URLs (PhiUSIIL dataset) |

### 4.3 Model Files

| File | Description |
|------|-------------|
| `data/processed/hybrid_model.pkl` | TF-IDF vectorizer + LR + SVM for text |
| `data/processed/url_models.pkl` | LR + SVM for URL phishing detection |

---

## 5. Datasets

### 5.1 Combined Text Dataset

| Source | Type | Messages | Labels |
|--------|------|----------|--------|
| SMS Spam Collection (UCI) | English SMS | 5,574 | ham/spam |
| SMS Phishing (Mishra & Soni) | English SMS | 5,971 | ham/spam/smishing |
| jngb-labs/sms-spam (HF) | English SMS | 5,159 | ham/spam |
| ucirvine/sms_spam (HF) | English SMS | 5,574 | ham/spam |
| mshenoda/spam-messages (HF) | English multi-source | 47,392 | ham/spam |
| **Khmer custom** | **Khmer Telegram** | **1,078** | **spam=714, ham=364** |
| **Total** | | **52,405** | |

### 5.2 Khmer Dataset Breakdown

| Category | Count | Source |
|----------|-------|--------|
| Synthetic Khmer scam | 313 | Manually written by developer |
| Translated Khmer (Google API) | 600 | English → Khmer via Google Translate API |
| Investment scam (EN+KM) | 165 | Hand-crafted investment scam patterns |
| Ham (normal Khmer) | 364 | Safe chat messages |
| **Total** | **1,078** | |

### 5.3 URL Dataset

| Source | URLs | Labels |
|--------|------|--------|
| PhiUSIIL Phishing URL | 235,795 | phishing/legitimate |
| URLhaus (abuse.ch) | 13,759 | malware URLs |
| OpenPhish | 300 | phishing URLs |
| PhishTank | 76,677 | phishing URLs |

### 5.4 Hash Database

| Source | Hashes | Type |
|--------|--------|------|
| MalwareBazaar CSV | 1,762 | SHA256 malware hashes |

---

## 6. Feature Engineering

### 6.1 Text Features (Keyword Categories)

| Category | EN Keywords | KM Keywords | Example |
|----------|-------------|-------------|---------|
| URGENCY | 30+ words (urgent, immediately, suspended...) | 10 words (បន្ទាន់, ភ្លាមៗ, ឥឡូវនេះ...) | "Account suspended" |
| MONEY_BAIT | 100+ words (money, prize, invest, guarantee...) | 24 words (លុយ, ប្រាក់, ចំណេញ, បង្វិល...) | "Send $20 get $200" |
| CREDENTIAL_ASK | 50+ words (password, OTP, verify...) | 5 words (គណនី, ពាក្យសម្ងាត់, លេខកូដ...) | "Send your OTP code" |
| PAYMENT_SCAM | 18 patterns (payment failed, release fee...) | - | "Pay to unlock account" |
| FAMILY_SCAM | 14 words (grandma, accident, hospital...) | 6 words (ជួយខ្ញុំ, គ្រោះថ្នាក់...) | "Grandma in hospital" |
| JOB_BAIT | 10 words (job, salary, hire...) | 5 words (ការងារ, ប្រាក់ខែ...) | "Work from home $500" |

### 6.2 TF-IDF Features

- **Vectorizer:** `TfidfVectorizer(max_features=10000, ngram_range=(1,2), min_df=2, max_df=0.95, sublinear_tf=True)`
- **Combined with:** 11 binary keyword features via sparse hstack

### 6.3 URL Features (28 total)

| Feature | Description |
|---------|-------------|
| `url_length` | Total URL length |
| `domain_length` | Domain name length |
| `has_ip` | Domain is an IP address |
| `has_suspicious_tld` | TLD is .tk, .ml, .xyz, etc. |
| `suspicious_keyword_count` | Count of "login", "verify", "bank" in URL |
| `is_known_safe_domain` | Whitelist check (40+ domains) |
| `entropy` | Shannon entropy of URL string |
| `subdomain_depth` | Number of subdomains |
| `has_https` | HTTPS enabled |
| + 19 more | Dots, hyphens, digits ratio, etc. |

### 6.4 File Features

| Feature | Description |
|---------|-------------|
| `ext_exec` | Extension is executable (exe, scr, bat, etc.) |
| `ext_archive` | Extension is archive (zip, rar, 7z) |
| `double_ext` | Double extension (e.g. `invoice.pdf.exe`) |
| Magic bytes | Real file type from header bytes |
| Extension mismatch | Declared ext ≠ actual type |

---

## 7. Bot Capabilities

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with instructions |
| `/check` | Reply to a message to scan it |
| `/hash <sha256>` | Check file hash against MalwareBazaar DB |

### Handlers

| Handler | Trigger | Action |
|---------|---------|--------|
| Text handler | Any text message | Scans for scam patterns + URLs |
| Document handler | File sent to bot | Checks file name, extension, magic bytes |
| Photo handler | Photo sent | Basic text extraction from caption |

### Group Behavior

In groups, the bot only responds when:
1. A message is a reply to the bot
2. The bot is mentioned (`@botname`)
3. A document/file is sent
4. A message contains a URL
5. A message contains suspicious keywords (60+ keywords in EN+KM)

### Report Format

```
🚫 **គ្រោះថ្នាក់ (85%)**

⏰ ប្រើពាក្យដាក់សម្ពាធ (បន្ទាន់, ភ្លាមៗ)
💰 និយាយពីលុយ, រង្វាន់, ឬឆ្នោត
🔑 សូមពាក្យសម្ងាត់, OTP, ឬព័ត៌មានចូល

💡 **អនុសាសន៍:**
🚫 សារនេះគ្រោះថ្នាក់!
កុំបើកឯកសារ ឬចុចតំណភ្ជាប់!
សូមសួរអ្នកផ្ញើតាមប្រព័ន្ធផ្សេង។
```

---

## 8. Detection Pipeline

### Text Message Flow

```
1. Extract text from message
2. Extract URLs from text
3. For each URL:
   a. Check safe domain whitelist → if safe, skip
   b. Extract 28 URL features
   c. Run LR + SVM → phishing probability
4. For text content:
   a. Match keyword categories (urgency, money_bait, etc.)
   b. TF-IDF transform → LR + SVM prediction
   c. Combine: keyword_score + ml_score
5. If file attached:
   a. Check extension against executable/archive lists
   b. If ZIP: inspect contents for .exe files
   c. If bytes available: magic byte check + extension mismatch
6. Generate report in Khmer with risk level, score, reasons
```

### File Check Flow

```
1. Get file metadata (name, size, mime type)
2. Check extension:
   - Executable (.exe, .scr, .bat...) → high risk
   - Archive (.zip, .rar, .7z) → check contents
   - Document (.pdf, .docx, .jpg...) → safe
3. If ZIP file:
   - Open and list all files inside
   - Check for .exe files inside archive
   - Check for double extensions (e.g. document.pdf.exe)
4. If raw bytes available:
   - Read magic bytes (first 4-8 bytes)
   - Compare declared extension vs actual type
   - Flag mismatches (e.g. file named .pdf but is .exe)
5. Hash lookup:
   - SHA256 hash against local MalwareBazaar DB (1,762 hashes)
   - If found → report malware type and signature
```

---

## 9. Setup & Deployment

### Requirements

```
pandas>=2.0
scikit-learn>=1.3
python-telegram-bot>=21.0
requests>=2.31
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Fix numpy/scipy compatibility
pip install "scipy<1.14" "numpy<2"
```

### Train Models

```bash
# Train hybrid text model (TF-IDF + keywords → LR + SVM)
python3 src/train_hybrid.py
```

### Run Bot

```bash
# Start bot in screen session
screen -dmS scamguard bash start_bot.sh

# Check if running
pgrep -f "bot.main"

# View logs
tail -f /tmp/bot.log
```

### Docker (Testing Only)

```bash
# Run tests only (bot cannot run in Docker - no Telegram API access)
docker build -t scamguard .
docker run --rm scamguard
```

---

## 10. Testing Results

### Khmer Investment Scam (100 messages)

| Metric | Result |
|--------|--------|
| Detected | **100/100 (100%)** |
| False positives on safe Khmer | **0/10** |

### English Scam (120 messages)

| Metric | Result |
|--------|--------|
| Detected | **119/120 (99%)** |
| False positives on safe English | **0/10** |

### Mixed Language Investment Scam (100 messages)

| Metric | Result |
|--------|--------|
| Detected | **94/100 (94%)** |

### Safe Messages (20 messages)

| Metric | Result |
|--------|--------|
| Correctly classified safe | **20/20 (100%)** |

---

## 11. Project Structure

```
Telegram/
├── agent.md                 # Project brief and dataset catalog
├── requirements.txt         # Python dependencies
├── Dockerfile              # Test runner (not for production)
├── start_bot.sh            # Bot launch script
├── README.md               # This file
│
├── src/
│   ├── features.py         # Keyword lists + feature extraction
│   ├── train_hybrid.py     # Hybrid model training
│   ├── train_text_model.py # Legacy text model training
│   └── train_url_model.py  # URL model training
│
├── bot/
│   ├── __init__.py
│   ├── main.py             # Telegram bot entry point
│   ├── predict.py          # Hybrid text prediction
│   ├── url_predict.py      # URL phishing prediction
│   ├── url_features.py     # 28 URL features
│   ├── report.py           # Khmer/English report formatting
│   ├── deep_check.py       # Magic bytes + extension check
│   ├── zip_check.py        # ZIP contents inspection
│   └── hash_lookup.py      # Local SHA256 hash lookup
│
├── tests/
│   └── test_features.py    # Unit tests
│
└── data/
    ├── raw/
    │   ├── combined_spam_ham.csv    # 52,405 combined messages
    │   ├── khmer_scam_full.csv      # 1,078 Khmer messages
    │   ├── sms_spam.csv             # 5,572 SMS spam/ham
    │   ├── phiusiil.csv             # 235,796 URL dataset
    │   ├── malwarebazaar.csv        # 1,766 malware hashes
    │   ├── urlhaus.csv              # 13,759 malware URLs
    │   ├── openphish.txt            # 300 phishing URLs
    │   └── datasets/                # Downloaded HuggingFace datasets
    │
    └── processed/
        ├── hybrid_model.pkl         # Text ML model (TF-IDF + keywords → LR + SVM)
        └── url_models.pkl           # URL ML model (LR + SVM)
```

---

## 12. Limitations

| Limitation | Impact |
|------------|--------|
| Khmer dataset is mostly synthetic/translated | Model may not capture natural Khmer scam patterns |
| No Khmer tokenization (khmernltk unavailable) | Using character-level TF-IDF instead of word-level |
| Keywords are manually curated | New scam patterns may be missed until keywords are added |
| No real-time URL scanning | Only checks against pre-trained features, not live content |
| No file content analysis | Only inspects metadata (name, extension, magic bytes) |
| ML accuracy ~95% | Some edge cases will be missed or falsely flagged |
| Google Translate API rate-limited | Khmer dataset expansion is slow |
| Bot runs outside Docker | Requires manual process management via screen |

---

## References

### A. Phishing URL Datasets

| # | Dataset | Authors | Size | Citation | Download URL |
|---|---------|---------|------|----------|--------------|
| 1 | PhiUSIIL Phishing URL Dataset | Prasad, A. & Chandra, S. | 235,795 URLs | "PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning." *Computers & Security*, vol. 136, 103545, 2024. DOI: [10.1016/j.cose.2023.103545](https://doi.org/10.1016/j.cose.2023.103545) | [UCI ML Repository](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset), [Mendeley Data](https://data.mendeley.com/datasets/shwpxscxy2/2), [Kaggle](https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset) |
| 2 | PhishTank | PhishTank / OpenDNS | 76,677+ URLs | "PhishTank - Collaborative Anti-Phishing Data." | [phishtank.org](https://www.phishtank.com/developer_info.php), [CSV Feed](http://data.phishtank.com/data/online-valid.csv) |
| 3 | OpenPhish | OpenPhish | 300+ URLs | "OpenPhish - Phishing Intelligence." | [openphish.com](https://openphish.com/) |
| 4 | UCI Phishing Dataset | Garera, S. & Provos, N. | 11,055 URLs | "A Framework for Detection and Measurement of Phishing Attacks." *Proceedings of WORM*, 2007. | [UCI ML Repository](https://archive.ics.uci.edu/dataset/327/phishing+websites) |
| 5 | PhishStorm | Marchal, S. et al. | 48,236 URLs | "PhishStorm: Detecting Phishing With Streaming Analytics." *IEEE TDSC*, vol. 14, no. 6, 2017. DOI: [10.1109/TDSC.2016.2601294](https://doi.org/10.1109/TDSC.2016.2601294) | [IEEE DataPort](https://ieee-dataport.org/open-access/phishstorm-phishinglegitimate-url-dataset) |

### B. Malware URL / Malware Datasets

| # | Dataset | Authors | Size | Citation | Download URL |
|---|---------|---------|------|----------|--------------|
| 6 | URLhaus | abuse.ch | 13,759+ URLs | "URLhaus - Malware URL Exchange." abuse.ch, 2018-. | [urlhaus.abuse.ch](https://urlhaus.abuse.ch/), [CSV Feed](https://urlhaus.abuse.ch/downloads/csv_online/) |
| 7 | MalwareBazaar | abuse.ch | 1,762+ samples | "MalwareBazaar Project." abuse.ch, 2019-. | [bazaar.abuse.ch](https://bazaar.abuse.ch/), [Export CSV](https://bazaar.abuse.ch/export/) |
| 8 | VirusShare | Harrisburg University | 33M+ samples | "VirusShare - Because sometimes the bad guys need a friend." | [virusshare.com](https://virusshare.com/) |
| 9 | SOREL-20M | Russinovich, M. et al. (Microsoft) | 20M samples | "SOREL-20M: An Ransomware Dataset." 2022. DOI: [10.48550/arXiv.2202.00190](https://doi.org/10.48550/arXiv.2202.00190) | [GitHub](https://github.com/sophos-ai/SOREL-20M) |
| 10 | ANDRIMALWARE | Alasmary, M. et al. | 11,532 apps | "Andrimalware: An Android Malware Dataset." *IEEE S&P*, 2019. | [IEEE DataPort](https://ieee-dataport.org/open-access/andrimalware) |

### C. SMS/Text Spam & Phishing Datasets

| # | Dataset | Authors | Size | Citation | Download URL |
|---|---------|---------|------|----------|--------------|
| 11 | SMS Spam Collection (UCI) | Almeida, T.A., Hidalgo, J.M.G. & Yamakami, A. | 5,574 SMS | "Contributions to the study of SMS spam filtering: new collection and results." *Proceedings of the 11th ACM Symposium on Document Engineering*, pp. 259-262, 2011. | [UCI ML Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), [Kaggle](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) |
| 12 | SMS Phishing (Mishra & Soni) | Mishra, S. & Soni, D. | 5,971 SMS | "SMS Phishing Dataset for Machine Learning and Pattern Recognition." *Mendeley Data*, V1, 2022. DOI: [10.17632/f45bkkt8pr.1](https://doi.org/10.17632/f45bkkt8pr.1). Paper: *Proceedings of SoCPaR 2022*, LNNS vol. 648, pp. 597-604. DOI: [10.1007/978-3-031-27524-1_57](https://doi.org/10.1007/978-3-031-27524-1_57) | [Mendeley Data](https://data.mendeley.com/datasets/f45bkkt8pr/1) |
| 13 | Super SMS Spam Corpus | - | 153,551 SMS | "Super spam corpus: An extensive and enriched SMS spam dataset." 2022. | [arXiv:2210.10451](https://arxiv.org/abs/2210.10451) |
| 14 | BangalaBarta | - | 2,772 SMS | Bangla SMS spam/smishing dataset with 3-class labeling. | [Mendeley Data](https://data.mendeley.com/datasets/jfkfbw3gzh/3) |
| 15 | Nigerian Fraud SMS | - | 4,000+ SMS | Nigerian advance-fee fraud SMS messages. | [Kaggle](https://www.kaggle.com/datasets/rtatman/fraudulent-email-corpus) |
| 16 | Enron Spam Dataset | Metsis, V. et al. | 33,716 emails | "Spam Filtering with Naive Bayes - Which Naive Bayes?" *Proceedings of CEAS 2006*. | [Kaggle](https://www.kaggle.com/datasets/wanderfj/enron-spam) |
| 17 | Ling-Spam Corpus | Androutsopoulos, I. et al. | 2,893 emails | "An Experimental Study of Naive Bayes Filtering in the Context of E-mail Anti-Spam." 2000. | [SourceForge](https://sourceforge.net/projects/ling-spam/) |

### D. Khmer NLP Datasets

| # | Dataset | Authors | Size | Citation | Download URL |
|---|---------|---------|------|----------|--------------|
| 18 | khPOS | SeACrowd | 12,000 sentences | Khmer part-of-speech tagged corpus from news/web sources. | [HuggingFace](https://huggingface.co/datasets/SEACrowd/khpos) |
| 19 | khmer_alt_pos | Kaing et al. | 20,000 sentences | "Khmer Word Segmentation and Part-of-Speech Tagging." *ACM TALLIP*, vol. 20, no. 6, 2021. DOI: [10.1145/3464378](https://doi.org/10.1145/3464378) | [HuggingFace](https://huggingface.co/datasets/SEACrowd/khmer_alt_pos) |
| 20 | kheed_annotated | CADT-IDRI | 1K-10K rows | Khmer token-classification dataset, CC-BY-SA-4.0. | [HuggingFace](https://huggingface.co/datasets/CADT-IDRI/kheed_annotated) |
| 21 | Khmer FastText Sentiment | tykea | - | Binary sentiment classifier using khmernltk. | [HuggingFace](https://huggingface.co/tykea/khmer-fasttext-sentiment-analysis) |
| 22 | Khmer RoBERTa | seanghay | - | Khmer text classification using RoBERTa. | [HuggingFace](https://huggingface.co/seanghay/khmer-text-classification-roberta) |

### E. Telegram-Specific Research

| # | Paper | Authors | Year | Citation | URL |
|---|-------|---------|------|----------|-----|
| 23 | "Cryptocurrency Pump-and-Dump Schemes in Telegram" | Li, T. et al. | 2019 | Analysis of pump-and-dump schemes on Telegram crypto channels. | [arXiv:1902.03110](https://arxiv.org/abs/1902.03110) |
| 24 | "Fake Channels on Telegram" | Wu, J. et al. | 2021 | Study of fake/malicious Telegram channels. | [PDF](https://cis.temple.edu/~jiewu/research/publications/Publication_files/Telegram_ICWS.pdf) |
| 25 | "TeleScope: Longitudinal Telegram Dataset" | Guo, Y. et al. | 2025 | Large-scale longitudinal Telegram dataset for research. | [arXiv:2603.24302](https://arxiv.org/abs/2603.24302) |
| 26 | "Measuring and Mitigating Telegram Scam" | - | 2023 | Framework for detecting scam campaigns on Telegram. | [IEEE Xplore](https://ieeexplore.ieee.org/) |

### F. Khmer News Classification (Related Work)

| # | Paper | Authors | Year | Citation | URL |
|---|-------|---------|------|----------|-----|
| 27 | "Khmer News Classification using TF-IDF and XLM-RoBERTa" | Korat, N., Sopagna, H. & Vathna, L. (CADT) | 2025 | Compares TF-IDF+SVM with XLM-RoBERTa and LaBSE on 7,344 Khmer news articles. | DOI: [10.32913/mic-ict-research-vn.1377](https://doi.org/10.32913/mic-ict-research-vn.1377), [PDF](https://ictmag.ictvietnam.vn/cntt-tt/article/download/1377/628/) |

### G. Tools & Libraries

| # | Tool | Purpose | Citation | URL |
|---|------|---------|----------|-----|
| 28 | scikit-learn | ML models (Logistic Regression, Linear SVM, TF-IDF) | Pedregosa, F. et al. (2011). "Scikit-learn: ML in Python." *JMLR* 12, 2825-2830. | [scikit-learn.org](https://scikit-learn.org/), [GitHub](https://github.com/scikit-learn/scikit-learn) |
| 29 | python-telegram-bot | Telegram Bot API wrapper | - | [GitHub](https://github.com/python-telegram-bot/python-telegram-bot), [pypi](https://pypi.org/project/python-telegram-bot/) |
| 30 | pandas | Data manipulation | McKinney, W. (2010). "Data Structures for Statistical Computing." *Proceedings of SciPy 2010*, 51-56. | [pandas.pydata.org](https://pandas.pydata.org/), [GitHub](https://github.com/pandas-dev/pandas) |
| 31 | NumPy | Numerical computing | Harris, C.R. et al. (2020). "Array programming with NumPy." *Nature* 585, 357-362. DOI: [10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2) | [numpy.org](https://numpy.org/), [GitHub](https://github.com/numpy/numpy) |
| 32 | SciPy | Scientific computing | Virtanen, P. et al. (2020). "SciPy 1.0: Fundamental Algorithms for Scientific Computing." *Nature Methods* 17, 261-272. DOI: [10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2) | [scipy.org](https://scipy.org/), [GitHub](https://github.com/scipy/scipy) |
| 33 | Google Translate API | Khmer dataset translation | Used via `translate.googleapis.com` (free tier, no API key required) | [Google Cloud Translation](https://cloud.google.com/translate) |

---

## Credits

- **Datasets:** PhiUSIIL, URLhaus, MalwareBazaar, SMS Spam Collection (UCI), Mishra & Soni, HuggingFace community datasets
- **ML:** scikit-learn (Logistic Regression, Linear SVM, TF-IDF)
- **Bot:** python-telegram-bot library
- **Translation:** Google Translate API (for Khmer dataset creation)
