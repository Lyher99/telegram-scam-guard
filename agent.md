# Telegram Scam Guard (Khmer + English) - Project Brief and Dataset Catalog

Prepared: 2026-09-20. Audience: an AI coding/research agent that will help build the project and draft a research paper.
The human owner is a Cambodian developer (Python for ML, Node.js for bots). The finished tool may be hosted on their own web-utility site.

**Read section 0 first.** It says what is verified, what is not, and what you must never do.

---

## 0. Ground rules for the agent

1. **Never open, download, install or execute any suspicious file, and never visit any suspicious URL.** All work uses text and metadata only (message text, link text, file name, file size, reported type).
2. **Never download malware samples.** From MalwareBazaar use only the CSV metadata exports, never the sample-download API.
3. URLs inside URLhaus / PhishTank-style feeds may be live malware. Treat them as plain strings. Do not fetch them, do not put them in a browser, do not make them clickable in any output.
4. **Privacy:** never store or publish raw community messages. Remove phone numbers, names, usernames, bank/wallet numbers, ID numbers. Share code, statistics and a few approved examples only.
5. **Data honesty:** keep real and synthetic data separate. Synthetic or machine-generated data may be used for training experiments only if clearly labeled, and never in the test set. The owner's teacher requires **real data**; confirm before relying on self-collected data (see section 10).
6. **Verification status:** URLs marked `[SEEN]` appeared in web search results on 2026-09-20. URLs marked `[UNVERIFIED]` come from memory or inference; check them before use. Dataset sizes and column names come from the sources' own descriptions unless marked otherwise. Do not invent dataset details.
7. Check each dataset's license and citation rules before publishing anything.

---

## 1. Project summary

**Name:** Telegram Scam Guard.
**Problem:** In Cambodian Telegram communities, users receive scam links and fake files (for example `invoice.pdf.exe`) with pressure messages such as "please help check this file". Installing or running the file can take over the account.
**Goal:** a tool (Telegram bot and/or web page) that takes a message, link and file *metadata* and returns a risk level with human-readable reasons, in Khmer and English.

Example output:

```
Dangerous, 91%
- File name has a double extension (looks like a document but is a program)
- The message pushes you to open it urgently
Do not open it. Ask the sender through another channel.
```

**Outputs to predict** (see section 6 for details):
1. Risk level: `safe` / `suspicious` / `dangerous`
2. Reasons (list of triggered features)
3. File-lure check (fake document, archive lure, normal)
4. Scam type (optional, needs more data): `job_investment`, `prize_giveaway`, `fake_document`, `account_phishing`, `other`
5. Optional: "unsure, ask a human" flag when class probabilities are close.

**Non-goals:** deciding whether a file is truly malicious (needs hash lookup or sandbox), identifying malware families, detecting hijacked friend accounts, opening or scanning files.

**Why it is research-worthy:** no public labeled dataset of Khmer or Telegram scam messages was found. The owner's locally collected data (Khmer/Telegram) is a new contribution, and public English/URL datasets allow a cross-domain evaluation.

---

## 2. Data architecture

| Component | Input to model | Public data used for training | Local data (owner collects) |
|---|---|---|---|
| Text model | message text | Mishra & Soni SMS phishing; SMS Spam Collection; Khmer corpora as "safe" text | Khmer/Telegram scam and normal chat messages |
| Link model | URL string only | PhiUSIIL (URL column), URLhaus (malicious URL strings + tags) | Links from local messages |
| File-name model | file name, extension, size, mime | MalwareBazaar metadata CSV (malicious names/types) | Normal file names from consenting community members (names only) |
| Fusion | features from all three | - | Local test set |

Key design decision: **train on public data, test on the local Khmer/Telegram set** to measure domain shift. Keep the local set out of training for the headline result.

---

## 3. Dataset catalog

### 3.1 PhiUSIIL Phishing URL dataset (links)

- **Use:** legitimate vs phishing URL classification; train the link model using **URL string features only** (this project never fetches pages).
- **Size:** 235,795 rows: 134,850 legitimate and 100,945 phishing URLs. 54 columns.
- **Label:** `1` = legitimate, `0` = phishing. The `FILENAME` column can be ignored.
- **Links:**
  - UCI: https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset `[SEEN]`
  - Mendeley Data: https://data.mendeley.com/datasets/shwpxscxy2/2 `[SEEN]`
  - Kaggle: https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset `[SEEN]`
- **Load in Python:**
  ```python
  # pip install ucimlrepo
  from ucimlrepo import fetch_ucirepo
  d = fetch_ucirepo(id=967)
  X, y = d.data.features, d.data.targets
  ```
- **Citation:** Prasad, A., Chandra, S. (2024). PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning. Computers & Security, vol. 136, 103545. DOI: 10.1016/j.cose.2023.103545 (page: https://www.sciencedirect.com/science/article/abs/pii/S0167404823004558 `[SEEN]`).
- **Caveats:** papers using it report accuracy above 99%, so it is an "easy" benchmark. Use time or cross-dataset evaluation to avoid over-optimistic claims. Many original features are derived from webpage HTML; do **not** use those, because the deployed tool never opens pages.

### 3.2 URLhaus (abuse.ch) (malicious link strings + tags)

- **Use:** malicious URL strings (malware distribution) and tags such as file type (`exe`, `scr`, `7z`) and `password-protected`, useful for link and file-lure statistics.
- **Size:** roughly 3.8 million malicious URLs collected since 2018 (per a third-party description). Bulk CSV feeds exist.
- **Feed columns (seen in feed headers):** `Dateadded (UTC), URL, URL_status, Threat, Tags, Host, IPaddress, ASnumber, Country`.
- **Links:**
  - Home: https://urlhaus.abuse.ch/ `[SEEN]`
  - Feeds info: https://urlhaus.abuse.ch/feeds/ `[SEEN]`
  - Online-URL CSV: https://urlhaus.abuse.ch/downloads/csv_online/ `[SEEN]`
  - Free Auth-Key (needed for the API, possibly for bulk downloads): https://auth.abuse.ch `[SEEN]`
  - API: `POST https://urlhaus-api.abuse.ch/v1/` with header `Auth-Key` `[SEEN]`
- **Terms:** check abuse.ch terms on the site before publishing. Commercial use may need a paid plan.
- **Caveats:** data are generic malware distribution, not Telegram-specific. **Do not visit the URLs.** Class balance must be built by pairing with legitimate URLs (PhiUSIIL legitimate rows).

### 3.3 SMS Phishing Dataset (Mishra & Soni) (English text)

- **Use:** English text classification: ham / spam / smishing.
- **Size:** 5,971 messages: 4,844 ham, 489 spam, 638 smishing. Columns: `LABEL, TEXT, URL, EMAIL, PHONE`.
- **Link:** https://data.mendeley.com/datasets/f45bkkt8pr/1 `[SEEN]` (DOI 10.17632/f45bkkt8pr.1). Download manually from Mendeley.
- **Citation:** Mishra, S., Soni, D. (2022). SMS Phishing Dataset for Machine Learning and Pattern Recognition. Mendeley Data, V1, DOI 10.17632/f45bkkt8pr.1. Paper: Mishra, S. (2023), Proceedings of the 14th International Conference on Soft Computing and Pattern Recognition, LNNS vol. 648, pp. 597-604, DOI 10.1007/978-3-031-27524-1_57 (https://link.springer.com/chapter/10.1007/978-3-031-27524-1_57 `[SEEN]`).
- **Caveats:** smishing messages were collected by converting images found on the Internet to text, so expect OCR noise. It is English and SMS, not Telegram and not Khmer.

### 3.4 SMS Spam Collection (English text)

- **Use:** larger ham/spam baseline; pipeline testing.
- **Size:** 5,574 English messages: 4,827 ham, 747 spam.
- **Link:** https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset `[SEEN]`. Kaggle CLI: `kaggle datasets download -d uciml/sms-spam-collection-dataset` (needs a Kaggle API token).
- **Also:** UCI copy https://archive.ics.uci.edu/dataset/228/sms+spam+collection `[UNVERIFIED]`.
- **License:** one catalog listed "no known license". Check the UCI page and cite the authors (Almeida, Gomez Hidalgo, Yamakami, 2011, DocEng - `[UNVERIFIED]` citation details).
- **Caveats:** old (about 2011), English, mostly UK/Singapore-style SMS spam. Adequate for a baseline; not representative of current scams.

### 3.5 MalwareBazaar (abuse.ch) metadata (file names)

- **Use:** statistics of malicious file names, extensions, file types and mime types.
- **CSV columns (seen in the recent export):** `first_seen_utc, sha256_hash, md5_hash, sha1_hash, reporter, file_name, file_type_guess, mime_type, signature, clamav, vtpercent, imphash, ssdeep, tlsh`.
- **Links:**
  - Export page: https://bazaar.abuse.ch/export/ `[SEEN]` (needs a free Auth-Key via `auth-key` URI parameter; example: `curl -i "https://mb-api.abuse.ch/v2/files/exports/YOUR-AUTH-KEY-HERE/recent.csv"`)
  - Recent CSV: https://bazaar.abuse.ch/export/csv/recent `[SEEN]` (last 48 hours only; do not fetch more often than every 5 minutes; full dumps once per hour at most)
  - Terms: https://bazaar.abuse.ch/faq/ `[SEEN]`
  - Kaggle snapshot (metadata only, no binaries, CC BY 4.0 for the packaged metadata, taken 2025-09-27): https://www.kaggle.com/datasets/jeffborschowa/malwarebazaar-threat-intelligence-csv `[SEEN]`. Files: `Dataset1.csv` (all-time metadata), `Dataset2.csv` (latest ~30 days), `Dataset3.csv` (YARA rules). Read with `pd.read_csv(path, comment="#")`. Also honour the original MalwareBazaar terms.
- **Citation suggestion (from the snapshot page):** abuse.ch MalwareBazaar Project (2025). "Malware Metadata and YARA Rules - Snapshot Sept 27, 2025." Retrieved from MalwareBazaar (abuse.ch).
- **Caveats:** file names are mostly generic malware names (ELF, APK bundles, executables), not Telegram lure names, and many name fields can be `None`. **Metadata only. Never download samples.** Benign file names are not supplied: collect names (only names) from consenting community members or other legitimate sources, and state this in the paper. Commercial use of the API may require a paid subscription.

### 3.6 Khmer text (safe-side text, tokenization)

| Dataset | Content | Link | Status |
|---|---|---|---|
| khPOS | 12,000 sentences (25,626 words), from websites on economics, news, politics; the description says it also contains student and voter lists | https://huggingface.co/datasets/SEACrowd/khpos (page inferred from file URL `[SEEN]` .../khpos/blob/main/khpos.py) | Filter out name lists before any use |
| khmer_alt_pos | 20,000-sentence Khmer corpus with manual tokenization and POS tags; needs `pip install seacrowd` | https://huggingface.co/datasets/SEACrowd/khmer_alt_pos `[SEEN]` | Citation: Kaing et al. 2021, ACM TALLIP 20(6), DOI 10.1145/3464378 |
| kheed_annotated (CADT) | Khmer token-classification data, 1K-10K rows, CC-BY-SA-4.0, uploaded July 2025 | https://huggingface.co/datasets/CADT-IDRI/kheed_annotated (page inferred from file URL `[SEEN]`) | Clear license |
| Khmer text collection (gated) | Combination of 3 datasets; requires login and accepting conditions | https://huggingface.co/datasets/kimleang123/khmer-text-dataset `[SEEN]` | Read conditions first |
| Khmer collection list | Curated list of Khmer models/datasets | https://huggingface.co/collections/SoyVitou/khmer-text-685cf6f64014258eb79c624e `[SEEN]` | Browse for more |
| Khmer FastText sentiment model | Binary sentiment classifier; uses `khmernltk` `word_tokenize` | https://huggingface.co/tykea/khmer-fasttext-sentiment-analysis `[SEEN]` | Tool/reference, not scam data |
| Khmer text classification RoBERTa | Card not readable during research | https://huggingface.co/seanghay/khmer-text-classification-roberta `[SEEN]` | Check what it classifies |

**Important:** formal text (news, government sentences) is not chat text. If the "safe" class is mostly formal Khmer, the model learns "formal vs informal", not "safe vs scam". Mix in real consented chat messages, and make the **test set** fully real chat data.

**Do not use as real data:** `sailor2/sea-synthetic` (https://huggingface.co/datasets/sailor2/sea-synthetic `[SEEN]`, synthetic) and `guanvireak/khmer-nlp-technical-corpus` (https://huggingface.co/datasets/guanvireak/khmer-nlp-technical-corpus `[SEEN]`, generated text). Also avoid the LLM-generated balanced SMS dataset (https://data.mendeley.com/datasets/vmg875v4xs/1 `[SEEN]`, 10,191 synthetic messages).

Khmer NLP tips: normalize Unicode; Khmer has no spaces between words, so use character n-grams (`analyzer="char_wb", ngram_range=(2,5)`) or `khmernltk` for word segmentation.

### 3.7 Related work and leads (papers and datasets)

- Khmer news classification (CADT, 2025): Korat Natt, Heang Sopagna, Lay Vathna. Compares TF-IDF+SVM with XLM-RoBERTa and LaBSE on a self-collected set of 7,344 Khmer news articles. DOI 10.32913/mic-ict-research-vn.1377 `[SEEN]` (https://ictmag.ictvietnam.vn/cntt-tt/article/download/1377/628/). Public availability of the data is unknown; contact the authors. Useful as a precedent for methods and for self-collected Khmer data.
- Super SMS Spam corpus (153,551 SMS from public sources): arXiv 2210.10451 https://arxiv.org/pdf/2210.10451 `[SEEN]`. Download link not found; check the paper.
- BangalaBarta (Bangla spam/smishing, 2,772 SMS, 3 classes): https://data.mendeley.com/datasets/jfkfbw3gzh/3 `[SEEN]`. Same class design as this project; cite as a comparable dataset from a low-resource language.
- Telegram crypto pump-and-dump study: arXiv 1902.03110 https://arxiv.org/pdf/1902.03110 `[SEEN]` (crawler-based study).
- Fake channels on Telegram: https://cis.temple.edu/~jiewu/research/publications/Publication_files/Telegram_ICWS.pdf `[SEEN]`.
- TeleScope (longitudinal Telegram dataset, Guo et al. 2025): only seen as a citation inside arXiv 2603.24302; availability and license `[UNVERIFIED]`.
- Hugging Face `ealvaradob/phishing-dataset`: seen only as a citation described as containing the 5,971 SMS above; contents `[UNVERIFIED]`.
- PLOS ONE dengue early-warning paper is unrelated to this project (see appendix if pivoting).

### 3.8 Local Khmer/Telegram data (the new contribution)

Target for a first working version: about 350 messages (150 safe, 50 suspicious, 150 dangerous). For a paper, aim for 1,000 to 1,500 unique messages with at least 100 dangerous messages in the test set. Collect via consented community donations and the owner's own inbox. Use the labeling workbook `scam_guard_labeling.xlsx` and `LABELING_GUIDE.md` (delivered separately). Fields: id, date, source, platform, text, language, has_file, file_name, file_size_kb, file_mime, label, scam_type, evidence, confidence, consent, notes, template_group.

---

## 4. Label mapping across sources (document this in the paper)

| Source | Original label | Mapped to |
|---|---|---|
| Mishra & Soni | ham / spam / smishing | safe / suspicious / dangerous |
| SMS Spam Collection | ham / spam | safe / suspicious (no smishing split) |
| PhiUSIIL | 1 legitimate / 0 phishing | safe / dangerous |
| URLhaus | malware_download | dangerous |
| MalwareBazaar | any listed sample | dangerous (file-name model only) |
| Local data | labeled by owner with evidence field | safe / suspicious / dangerous |

State clearly that mappings are an assumption: "spam" is not the same thing as "suspicious", and every source has its own definition of scam.

---

## 5. Features (already implemented in `features.py`, delivered separately)

Text features: `urgency, money_bait, job_bait, prize_bait, help_check_bait, mentions_document, credential_ask, install_ask` (English and Khmer keyword lists; the Khmer lists must be reviewed by a Khmer speaker), `has_khmer, mixed_lang, text_len`.

Link features: `has_link, n_links, short_link, ip_link, tg_invite_link, link_punycode, link_long, link_exec_ext`.

File features: `has_file, ext_exec, ext_archive, double_ext, rlo_char` (hidden right-to-left override character), `space_gap` (many spaces before the extension), `mime_mismatch, password_archive, name_len, n_dots, file_size_kb`.

A rule baseline `rule_baseline(features)` returns a label plus reasons and is the first baseline to beat. Extension sets: executables (`exe scr bat cmd com msi js vbs jar apk lnk ps1 hta pif dll reg sh`), document names (`pdf doc docx xls xlsx ppt pptx jpg jpeg png gif txt mp4 mp3 csv rtf`), archives (`zip rar 7z iso img tar gz`).

---

## 6. Modeling plan

1. **Rule baseline** (from `features.py`).
2. **Logistic regression / linear SVM** on TF-IDF character n-grams of the text.
3. **Bayesian network (pgmpy)** on the discrete yes/no features. Suggested structure: `label` as the parent of each feature (Naive Bayes style), plus a few justified extra edges (for example `has_link -> short_link`, `job_bait -> money_bait`). Learn probabilities with `BayesianEstimator(prior_type="BDeu", equivalent_sample_size=5)`. Class name is `DiscreteBayesianNetwork` in newer pgmpy versions and `BayesianNetwork` in older ones. Do not learn the structure from a few hundred messages without checking stability; prefer a hand-designed structure.
4. **Optional:** a multilingual transformer (XLM-RoBERTa or LaBSE, both cover Khmer). With fewer than about 1,000 messages, use frozen embeddings plus logistic regression rather than full fine-tuning.
5. **Hybrid:** feed the text model's score into the Bayesian network as a discretized node.

**Evaluation protocol**
- Split by `template_group` or by date, **never randomly** (scammers reuse templates, and random splits inflate scores). Remove near-duplicates first.
- Keep at least 100 `dangerous` messages in the test set before trusting any number.
- Metrics: precision, recall, F1 for the dangerous class, confusion matrix, and calibration of probabilities. Report the cost trade-off between missed scams and false alarms.
- **Cross-domain test:** train on public data only, test on local Khmer/Telegram data; then train with a portion of local data and compare.
- **Learning curve:** train on 25/50/75/100% of local data and plot F1.
- **Label quality:** a second person labels 100 messages; report Cohen's kappa (`sklearn.metrics.cohen_kappa_score`). About 0.6-0.8 is reasonable.
- **Error analysis:** read at least 30 wrong predictions and categorize the failures.

**Bot output design:** risk level, probability, top reasons (Khmer and English), safe advice ("do not open; contact the sender another way"). Wording must say "looks risky", never "this is a scam".

---

## 7. Research paper outline

**Working title ideas:** "Metadata-Only Detection of Scam Messages and Fake-File Lures in Khmer Telegram Communities"; "A Low-Resource Scam Detector for Khmer: Cross-Domain Evaluation and Interpretable Models".

**Research questions**
- RQ1: How well do detectors trained on public English/URL data generalize to Khmer and Telegram scam messages?
- RQ2: Do file-name features (double extensions, archive lures) improve detection over text alone?
- RQ3: How does a Bayesian network compare with logistic regression and a transformer in accuracy, calibration and explainability?

**Structure:** Introduction; Related work (smishing datasets, phishing URL detection, Khmer NLP, Telegram scams); Data (public sources, local collection, consent and privacy, label mapping); Method (features, models, splits); Results (in-domain, cross-domain, ablations, learning curve); Error analysis; Discussion; Limitations; Ethics statement; Data and code availability (share code, feature tables and statistics, not raw messages).

**Limitations to state:** scam styles change quickly; the community sample may not represent all Cambodian users; metadata cannot prove maliciousness; labels are partly subjective; some public sets are old, English or OCR-derived; URL benchmarks are easy.

---

## 8. Task list for the agent (in order)

1. Create a Python environment: `pip install pandas scikit-learn pgmpy openpyxl ucimlrepo khmernltk datasets kaggle matplotlib`. Optional: `seacrowd`, `transformers`, `torch`.
2. Write `data/README.md` listing each dataset, its URL, license and access date. The owner downloads gated or login-only sources manually (Mendeley, Kaggle, Hugging Face gated sets, abuse.ch Auth-Key).
3. Write loaders that convert each source into one schema: `text, url, file_name, file_size_kb, mime, label, source_dataset, language, split_group`. Apply the label mapping in section 4. Log row counts and class balance.
4. Import the owner's labeling sheet (`scam_guard_labeling.xlsx`, sheet `Messages`, skip rows where `consent == "example"`).
5. Run `features.py` feature extraction on all sources; keep the raw text out of committed files.
6. Train and evaluate the baselines and the Bayesian network with the protocol in section 6. Save metrics as CSV and figures as PNG.
7. Run the cross-domain experiment and the learning curve.
8. Build the Telegram bot (Node.js or Python) that accepts forwarded text plus file metadata only, and never downloads files. Reply in Khmer and English with reasons.
9. Draft the paper from the outline in section 7, with citations from section 3.
10. Produce a reproducibility checklist and a data statement.

**Acceptance criteria:** no step opens files or URLs; all metrics computed on a split-by-template or split-by-date test set; the local test set has at least 100 dangerous messages before any headline accuracy is claimed; every dataset has license and citation recorded.

---

## 9. Suggested repository layout

```
scam-guard/
  README.md
  data/README.md            # dataset catalog + access dates (no raw private data)
  data/raw/                 # ignored by git
  data/processed/           # feature tables only
  src/features.py           # provided
  src/load_public.py
  src/load_local.py
  src/train_baselines.py
  src/train_bayes.py
  src/evaluate.py
  bot/                      # Telegram bot (metadata only)
  paper/                    # outline, figures, references.bib
  LABELING_GUIDE.md
```

Add `data/raw/` and any spreadsheet containing real messages to `.gitignore`.

---

## 10. Open questions for the human owner

1. Does the teacher accept locally collected community data together with public datasets? (The original requirement was real data from a public source. If not accepted, use only the public parts in sections 3.1-3.6, or switch to a backup project in the appendix.)
2. Consent process for donors: use the message in `LABELING_GUIDE.md`; have a Khmer speaker review the Khmer wording and the Khmer keyword lists in `features.py`.
3. Which platform first: Telegram bot, web page, or both?

---

## Appendix A. Backup project options with verified public data (if a pivot is needed)

| Project | Data | Link | Notes |
|---|---|---|---|
| Cambodia food price forecaster | WFP "Cambodia - Food Prices" on HDX | https://data.humdata.org/dataset/wfp-food-prices-for-cambodia `[SEEN]` | Time period seen: 2003-01-15 to 2024-06-15; monthly updates; license "Creative Commons Attribution for Intergovernmental Organisations"; contributors: WFP, source includes Cambodia's Agricultural Marketing Office via FAO. Columns (per another catalog): date, province, district, market, category, commodity, unit, priceflag, pricetype, currency, price (KHR), usdprice |
| Rainfall by province | CHIRPS-based dekadal indicators, HDX | https://data.humdata.org/dataset/khm-rainfall-subnational `[SEEN]` | Can be joined with food prices |
| Tourist arrivals | Cambodia open data portal (economy and finance) | https://data.mef.gov.kh/datasets/pd_67f64166dbc953000126f580 `[SEEN]` | Title says 2019-2024; check granularity |
| Cambodian open data APIs | NBC exchange rate, CSX, weather, AQI | https://data.mef.gov.kh/ `[SEEN]` | Mostly current feeds; collect history yourself |
| Cambodia HDX group | Rainfall, climate, trade, human development indicators | https://data.humdata.org/group/khm `[SEEN]` | Browse for more |
| Dengue early warning | OpenDengue global dengue counts | https://opendengue.org/data.html `[SEEN]` | Confirm Cambodia coverage and resolution first |
| Restock forecasting (retail, real) | Iowa Liquor Sales 2025 (CC BY 4.0), state of Iowa | https://catalog.data.gov/dataset/iowa-liquor-sales-2025 `[SEEN]`; CSV https://idh-be.iowa.gov/api/v1/datasets/1262/rows.csv `[SEEN]`; dataset page https://data.iowa.gov/catalog/dataset/1262 `[SEEN]` | Large file; process in chunks; 12 months per product |
| Restock forecasting (monthly) | Montgomery County MD "Warehouse and Retail Sales" | https://data.montgomerycountymd.gov/Community-Recreation/Warehouse-and-Retail-Sales/v76h-r7br/data `[SEEN]` | Monthly by item; check date range; portal terms apply |
| Retail with customer IDs | Online Retail II (UCI id 502) | `fetch_ucirepo(id=502)`; page https://archive.ics.uci.edu/dataset/502/online+retail+ii `[UNVERIFIED]` | UK online retailer, about 2 years |
| Grocery demand | Favorita (Kaggle competitions) | https://www.kaggle.com/c/favorita-grocery-sales-forecasting `[SEEN]`; https://www.kaggle.com/competitions/store-sales-time-series-forecasting `[UNVERIFIED]` | Kaggle login required |
| Safe-file / Khmer text | see section 3.6 | | |

---

## Appendix B. Verification log

- Verified by web search on 2026-09-20: PhiUSIIL details and citation; SMS Phishing (Mishra & Soni) composition and DOI; SMS Spam Collection size (via a paper's description); MalwareBazaar export page, CSV columns, Kaggle snapshot description; URLhaus feed columns and description; Khmer datasets listed in section 3.6; WFP food prices HDX page (fetched); Iowa Liquor Sales 2025 catalog page (fetched).
- Not verified: file contents of any dataset (nothing was downloaded), exact column names of the PhiUSIIL/Mishra CSV files beyond what their pages state, licenses not stated above, UCI SMS Spam page URL, Online Retail II URL, Kaggle Store Sales slug, TeleScope availability, HF `ealvaradob/phishing-dataset` contents.
- No public labeled Khmer or Telegram scam-message dataset was found in the search.
