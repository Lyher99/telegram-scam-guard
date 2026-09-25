import os
import re
import csv
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_phishtank():
    urls = []
    try:
        path = os.path.join(RAW_DIR, "phishtank.csv")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    url = row[1].strip()
                    if url.startswith("http"):
                        urls.append(url)
    except Exception as e:
        logger.error(f"PhishTank error: {e}")
    return urls


def load_openphish():
    urls = []
    try:
        path = os.path.join(RAW_DIR, "openphish.txt")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                url = line.strip()
                if url.startswith("http"):
                    urls.append(url)
    except Exception as e:
        logger.error(f"OpenPhish error: {e}")
    return urls


def load_urlhaus():
    urls = []
    try:
        path = os.path.join(RAW_DIR, "urlhaus.csv")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 3:
                    continue
                if len(row) >= 2:
                    url = row[1].strip()
                    if url.startswith("http"):
                        urls.append(url)
    except Exception as e:
        logger.error(f"URLhaus error: {e}")
    return urls


SAFE_URLS = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.github.com",
    "https://www.stackoverflow.com",
    "https://www.wikipedia.org",
    "https://www.reddit.com",
    "https://www.linkedin.com",
    "https://www.apple.com",
    "https://www.microsoft.com",
    "https://www.amazon.com",
    "https://www.netflix.com",
    "https://www.twitch.tv",
    "https://www.tiktok.com",
    "https://www.whatsapp.com",
    "https://www.telegram.org",
    "https://www.openai.com",
    "https://www.python.org",
    "https://www.djangoproject.com",
    "https://www.flask.palletsprojects.com",
    "https://www.fastapi.tiangolo.com",
    "https://www.heroku.com",
    "https://www.vercel.com",
    "https://www.netlify.com",
    "https://www.cloudflare.com",
    "https://www.mozilla.org",
    "https://www.wikipedia.org/wiki/Main_Page",
    "https://news.ycombinator.com",
    "https://medium.com",
    "https://dev.to",
    "https://www.freecodecamp.org",
    "https://www.codecademy.com",
    "https://www.coursera.org",
    "https://www.edx.org",
    "https://www.kaggle.com",
    "https://www.pypi.org",
    "https://docs.python.org",
    "https://realpython.com",
    "https://www.virustotal.com",
    "https://www.virustotal.com/gui/home/search",
    "https://www.virustotal.com/gui/file/abc123",
    "https://scanurl.net",
    "https://www.urlvoid.com",
    "https://www.spamhaus.org",
    "https://phishtank.org",
    "https://www.malwarebytes.com",
    "https://www.symantec.com",
    "https://www.kaspersky.com",
    "https://www.norton.com",
    "https://www.mcafee.com",
    "https://www.avg.com",
    "https://www.avast.com",
    "https://www.eset.com",
    "https://www.trendmicro.com",
    "https://www.bitdefender.com",
    "https://www.sophos.com",
    "https://www.paloaltonetworks.com",
    "https://www.crowdstrike.com",
    "https://www.zscaler.com",
    "https://www.okta.com",
    "https://www.auth0.com",
    "https://www.duosecurity.com",
    "https://www.pingidentity.com",
    "https://www.onelogin.com",
    "https://www.jumpcloud.com",
    "https://www.cyberark.com",
    "https://www.forescout.com",
    "https://www.armis.com",
    "https://www.iotsecurity101.com",
    "https://www.sans.org",
    "https://www.cisa.gov",
    "https://www.nist.gov",
    "https://www.ic3.gov",
    "https://www cybersecurity.gov",
    "https://attack.mitre.org",
    "https://www.exploit-db.com",
    "https://www.cvedetails.com",
    "https://www.shodan.io",
    "https://censys.io",
    "https://www.hackerone.com",
    "https://www.bugcrowd.com",
    "https://www.synack.com",
    "https://www.intigriti.com",
    "https://www.yoursecure.cloud",
    "https://www.acunetix.com",
    "https://www.burpsuite.com",
    "https://www.nmap.org",
    "https://www.wireshark.org",
    "https://www.metasploit.com",
    "https://www.owasp.org",
    "https://cheatsheetseries.owasp.org",
    "https://portswigger.net/web-security",
    "https://www.hackthebox.com",
    "https://www.tryhackme.com",
    "https://www.pentesterlab.com",
    "https://www.vulnhub.com",
    "https://www.overthewire.org",
    "https://www.root-me.org",
    "https://www.cryptopals.com",
    "https://www.coursera.org/learn/cryptography",
    "https://www.edx.org/learn/cybersecurity",
    "https://www.udemy.com/course/ethical-hacking",
    "https://www.pluralsight.com/courses/penetration-testing",
    "https://www.safaribooksonline.com",
    "https://www.oreilly.com",
    "https://www.amazon.com/dp/B08N5WRWNW",
    "https://www.ebay.com/itm/123456",
    "https://www.walmart.com/ip/123456",
    "https://www.target.com/p/123456",
    "https://www.bestbuy.com/site/123456",
    "https://www.homedepot.com/p/123456",
    "https://www.lowes.com/pd/123456",
    "https://www.costco.com/product.html",
    "https://www.etsy.com/listing/123456",
    "https://www.shopify.com",
    "https://www.woocommerce.com",
    "https://www.bigcommerce.com",
    "https://www.squarespace.com",
    "https://www.wix.com",
    "https://www.weebly.com",
    "https://www.jimdo.com",
    "https://www.godaddy.com",
    "https://www.namecheap.com",
    "https://www.cloudflare.com/dns",
    "https://www.route53.aws.amazon.com",
    "https://www.digitalocean.com",
    "https://www.linode.com",
    "https://www.vultr.com",
    "https://www.hetzner.com",
    "https://www.ovh.com",
    "https://www.rackspace.com",
    "https://www.ibm.com/cloud",
    "https://cloud.google.com",
    "https://azure.microsoft.com",
    "https://aws.amazon.com",
    "https://www.oracle.com/cloud",
    "https://www.salesforce.com",
    "https://www.zoho.com",
    "https://www.freshworks.com",
    "https://www Zendesk.com",
    "https://www.intercom.com",
    "https://www.drift.com",
    "https://www.hubspot.com",
    "https://www.marketo.com",
    "https://www.pardot.com",
    "https://www.mailchimp.com",
    "https://www.sendgrid.com",
    "https://www.twilio.com",
    "https://www.nexmo.com",
    "https://www.plivo.com",
    "https://www.messagebird.com",
    "https://www.sinch.com",
    "https://www.vonage.com",
]

DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "twitter.com",
    "instagram.com", "github.com", "stackoverflow.com", "wikipedia.org",
    "reddit.com", "linkedin.com", "apple.com", "microsoft.com",
    "amazon.com", "netflix.com", "twitch.tv", "tiktok.com",
    "whatsapp.com", "telegram.org", "openai.com", "python.org",
    "mozilla.org", "cloudflare.com", "medium.com", "dev.to",
    "heroku.com", "vercel.com", "netlify.com", "virustotal.com",
    "kaspersky.com", "symantec.com", "norton.com", "mcafee.com",
    "malwarebytes.com", "eset.com", "bitdefender.com", "sophos.com",
    "crowdstrike.com", "zscaler.com", "paloaltonetworks.com",
    "cisa.gov", "nist.gov", "sans.org", "owasp.org",
    "hackthebox.com", "tryhackme.com", "nmap.org", "shodan.io",
    "paypal.com", "stripe.com", "square.com", "braintree.com",
    "shopify.com", "woocommerce.com", "bigcommerce.com",
    "aws.amazon.com", "cloud.google.com", "azure.microsoft.com",
    "heroku.com", "digitalocean.com", "linode.com", "vultr.com",
    "slack.com", "discord.com", "zoom.us", "teams.microsoft.com",
    "dropbox.com", "drive.google.com", "onedrive.live.com",
    "icloud.com", "mega.nz", "mediafire.com",
]


def generate_safe_urls(n=5000):
    import random
    urls = list(SAFE_URLS)
    paths = [
        "/", "/about", "/contact", "/help", "/settings", "/profile",
        "/dashboard", "/api/v1/users", "/blog/2024/01/post", "/docs/getting-started",
        "/login", "/signup", "/pricing", "/features", "/products",
        "/search?q=test", "/item/12345", "/user/john", "/posts/abc123",
        "/download", "/upload", "/install", "/buy", "/subscribe",
        "/learn/python", "/course/101", "/tutorial/beginner",
    ]
    query_params = [
        "", "?q=test", "?id=123", "?ref=home", "?utm_source=google",
        "?page=1", "?sort=date", "?lang=en", "?v=abc123",
    ]
    subdomains = ["", "www.", "app.", "api.", "docs.", "blog.", "shop."]
    for _ in range(n - len(SAFE_URLS)):
        domain = random.choice(DOMAINS)
        sub = random.choice(subdomains)
        path = random.choice(paths)
        query = random.choice(query_params)
        scheme = random.choice(["https://", "http://"])
        urls.append(f"{scheme}{sub}{domain}{path}{query}")
    return urls


def extract_features(url):
    from urllib.parse import urlparse
    import re
    import math

    try:
        parsed = urlparse(url)
    except Exception:
        return None

    domain = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    full = url

    features = {}
    features["url_length"] = len(full)
    features["domain_length"] = len(domain)
    features["path_length"] = len(path)
    features["query_length"] = len(query)
    features["num_dots"] = full.count(".")
    features["num_hyphens"] = full.count("-")
    features["num_underscores"] = full.count("_")
    features["num_slashes"] = full.count("/")
    features["num_at"] = full.count("@")
    features["num_question"] = full.count("?")
    features["num_equals"] = full.count("=")
    features["num_ampersand"] = full.count("&")
    features["num_percent"] = full.count("%")
    features["num_digits"] = sum(c.isdigit() for c in full)
    features["digit_ratio"] = features["num_digits"] / max(len(full), 1)
    features["has_ip"] = 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain) else 0
    features["has_port"] = 1 if parsed.port else 0
    features["has_https"] = 1 if parsed.scheme == "https" else 0
    features["has_http"] = 1 if parsed.scheme == "http" else 0
    features["has_at_sign"] = features["num_at"]
    features["has_double_slash_redirect"] = 1 if "//" in path else 0
    features["subdomain_depth"] = max(domain.count(".") - 1, 0)
    features["has_suspicious_tld"] = 1 if any(domain.endswith(t) for t in [".tk", ".ml", ".ga", ".cf", ".xyz", ".top", ".buzz"]) else 0
    features["suspicious_keyword_count"] = sum(1 for kw in ["login", "verify", "account", "banking", "secure", "update", "confirm", "password", "paypal", "apple", "microsoft", "google", "amazon", "facebook", "whatsapp", "telegram", "crypto", "bitcoin", "free", "claim"] if kw in full.lower())

    features["is_known_safe_domain"] = 1 if any(domain.endswith(d) for d in [
        "google.com", "youtube.com", "facebook.com", "twitter.com", "instagram.com",
        "github.com", "stackoverflow.com", "wikipedia.org", "reddit.com", "linkedin.com",
        "apple.com", "microsoft.com", "amazon.com", "netflix.com", "whatsapp.com",
        "telegram.org", "openai.com", "python.org", "mozilla.org", "cloudflare.com",
        "virustotal.com", "kaspersky.com", "symantec.com", "norton.com", "mcafee.com",
        "malwarebytes.com", "paypal.com", "stripe.com", "shopify.com",
        "aws.amazon.com", "cloud.google.com", "azure.microsoft.com",
        "slack.com", "discord.com", "zoom.us", "dropbox.com",
        "vercel.app", "netlify.app", "herokuapp.com", "github.io", "github.dev",
        "gitlab.io", "bitbucket.io", "firebaseapp.com", "web.app",
        "pages.dev", "workers.dev", "azurewebsites.net", "cloudfront.net",
        "amazonaws.com", "s3.amazonaws.com", "heroku.com", "railway.app",
        "render.com", "fly.io", "deno.dev", "supabase.co",
    ]) else 0

    features["has_long_path"] = 1 if len(path) > 50 else 0
    features["has_long_query"] = 1 if len(query) > 100 else 0

    freq = {}
    for c in full:
        freq[c] = freq.get(c, 0) + 1
    length = len(full)
    ent = 0
    for count in freq.values():
        p = count / length
        ent -= p * math.log2(p)
    features["entropy"] = round(ent, 3)

    return features


FEATURE_NAMES = [
    "url_length", "domain_length", "path_length", "query_length",
    "num_dots", "num_hyphens", "num_underscores", "num_slashes",
    "num_at", "num_question", "num_equals", "num_ampersand", "num_percent",
    "num_digits", "digit_ratio",
    "has_ip", "has_port", "has_https", "has_http", "has_at_sign",
    "has_double_slash_redirect",
    "subdomain_depth", "has_suspicious_tld", "suspicious_keyword_count",
    "is_known_safe_domain",
    "entropy", "has_long_path", "has_long_query",
]


def prepare_dataset():
    logger.info("Loading PhishTank...")
    phish_urls = load_phishtank()
    logger.info(f"PhishTank: {len(phish_urls)} URLs")

    logger.info("Loading OpenPhish...")
    openphish_urls = load_openphish()
    logger.info(f"OpenPhish: {len(openphish_urls)} URLs")

    logger.info("Loading URLhaus...")
    urlhaus_urls = load_urlhaus()
    logger.info(f"URLhaus: {len(urlhaus_urls)} URLs")

    all_phish = list(set(phish_urls + openphish_urls + urlhaus_urls))
    logger.info(f"Total phishing: {len(all_phish)}")

    safe_urls = generate_safe_urls(len(all_phish))
    logger.info(f"Safe URLs: {len(safe_urls)}")

    rows = []
    labels = []
    url_strings = []

    for url in all_phish:
        feat = extract_features(url)
        if feat:
            rows.append(feat)
            labels.append(1)
            url_strings.append(url)

    for url in safe_urls:
        feat = extract_features(url)
        if feat:
            rows.append(feat)
            labels.append(0)
            url_strings.append(url)

    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    df["label"] = labels
    df["url_string"] = url_strings

    os.makedirs(PROC_DIR, exist_ok=True)
    out_path = os.path.join(PROC_DIR, "url_dataset.csv")
    df.to_csv(out_path, index=False)
    logger.info(f"Dataset saved: {out_path} ({len(df)} rows)")

    return df


def train_model():
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import LinearSVC
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import VotingClassifier
    from sklearn.metrics import accuracy_score, classification_report
    import pickle

    df = prepare_dataset()

    X = df[FEATURE_NAMES].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    logger.info("Training LR on features...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_acc = accuracy_score(y_test, lr.predict(X_test))
    logger.info(f"LR accuracy: {lr_acc:.4f}")

    logger.info("Training SVM on features...")
    svm = LinearSVC(max_iter=1000, random_state=42)
    svm.fit(X_train, y_train)
    svm_acc = accuracy_score(y_test, svm.predict(X_test))
    logger.info(f"SVM accuracy: {svm_acc:.4f}")

    logger.info("Training TF-IDF on URL strings...")

    all_urls = df["url_string"].tolist()
    all_labels = df["label"].tolist()

    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(all_urls, all_labels, test_size=0.2, random_state=42, stratify=all_labels)

    tfidf = TfidfVectorizer(analyzer="char", ngram_range=(2, 5), max_features=5000)
    X_train_tfidf = tfidf.fit_transform(X_train_s)
    X_test_tfidf = tfidf.transform(X_test_s)

    lr_tfidf = LogisticRegression(max_iter=1000, random_state=42)
    lr_tfidf.fit(X_train_tfidf, y_train_s)
    lr_tfidf_acc = accuracy_score(y_test_s, lr_tfidf.predict(X_test_tfidf))
    logger.info(f"TF-IDF LR accuracy: {lr_tfidf_acc:.4f}")

    svm_tfidf = LinearSVC(max_iter=1000, random_state=42)
    svm_tfidf.fit(X_train_tfidf, y_train_s)
    svm_tfidf_acc = accuracy_score(y_test_s, svm_tfidf.predict(X_test_tfidf))
    logger.info(f"TF-IDF SVM accuracy: {svm_tfidf_acc:.4f}")

    print("\n" + "=" * 60)
    print("URL MODEL RESULTS")
    print("=" * 60)
    print(f"Feature LR:      {lr_acc:.4f}")
    print(f"Feature SVM:     {svm_acc:.4f}")
    print(f"TF-IDF LR:       {lr_tfidf_acc:.4f}")
    print(f"TF-IDF SVM:      {svm_tfidf_acc:.4f}")
    print("=" * 60)

    models = {
        "lr_features": lr,
        "svm_features": svm,
        "lr_tfidf": lr_tfidf,
        "svm_tfidf": svm_tfidf,
        "tfidf_vectorizer": tfidf,
        "feature_names": FEATURE_NAMES,
    }

    out_path = os.path.join(PROC_DIR, "url_models.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(models, f)
    logger.info(f"Models saved: {out_path}")

    print("\nClassification Report (Feature LR):")
    print(classification_report(y_test, lr.predict(X_test), target_names=["safe", "phishing"]))


if __name__ == "__main__":
    train_model()
