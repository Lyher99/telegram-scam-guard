import re
import math
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".buzz", ".club",
    ".work", ".live", ".online", ".site", ".info", ".biz", ".tech",
}

SUSPICIOUS_KEYWORDS = {
    "login", "signin", "verify", "account", "banking", "secure", "update",
    "confirm", "password", "credential", "suspend", "restrict", "urgent",
    "alert", "warning", "paypal", "apple", "microsoft", "google", "amazon",
    "facebook", "whatsapp", "telegram", "instagram", "netflix", "crypto",
    "bitcoin", "wallet", "metamask", "airdrop", "free", "claim", "reward",
}

SAFE_DOMAINS = {
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
}


def extract_url_features(url):
    features = {}

    try:
        parsed = urlparse(url)
    except Exception:
        return None

    domain = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    full = url

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
    features["tld"] = ""
    parts = domain.split(".")
    if len(parts) >= 2:
        features["tld"] = "." + parts[-1].lower()

    features["has_suspicious_tld"] = 1 if features["tld"] in SUSPICIOUS_TLDS else 0

    features["suspicious_keyword_count"] = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in full.lower())

    features["is_known_safe_domain"] = 1 if any(domain.endswith(d) for d in SAFE_DOMAINS) else 0

    features["entropy"] = _entropy(full)

    features["has_long_path"] = 1 if len(path) > 50 else 0
    features["has_long_query"] = 1 if len(query) > 100 else 0

    return features


def _entropy(text):
    if not text:
        return 0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    length = len(text)
    ent = 0
    for count in freq.values():
        p = count / length
        ent -= p * math.log2(p)
    return round(ent, 3)


def get_feature_names():
    return [
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
