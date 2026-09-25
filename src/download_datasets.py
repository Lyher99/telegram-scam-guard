import os
import sys
import pandas as pd
import requests

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)


def download_phiusiil():
    print("=== PhiUSIIL Phishing URL Dataset ===")
    try:
        from ucimlrepo import fetch_ucirepo
        d = fetch_ucirepo(id=967)
        X = d.data.features
        y = d.data.targets
        df = pd.concat([X, y], axis=1)
        path = os.path.join(RAW_DIR, "phiusiil.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to {path}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Label distribution:\n{y.value_counts().to_string()}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def download_urlhaus():
    print("\n=== URLhaus Online URLs ===")
    url = "https://urlhaus.abuse.ch/downloads/csv_online/"
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        from io import StringIO
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        header = lines[0]
        data = "\n".join(lines[1:])
        df = pd.read_csv(StringIO(header + "\n" + data))
        path = os.path.join(RAW_DIR, "urlhaus.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to {path}")
        print(f"  Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def download_sms_spam():
    print("\n=== SMS Spam Collection ===")
    url = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        import zipfile, io
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(os.path.join(RAW_DIR, "sms_spam"))
        df = pd.read_csv(
            os.path.join(RAW_DIR, "sms_spam", "SMSSpamCollection"),
            sep="\t", header=None, names=["label", "text"]
        )
        path = os.path.join(RAW_DIR, "sms_spam.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to {path}")
        print(f"  Label distribution:\n{df['label'].value_counts().to_string()}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def download_malwarebazaar():
    print("\n=== MalwareBazaar Recent Metadata ===")
    url = "https://bazaar.abuse.ch/export/csv/recent"
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        from io import StringIO
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        if len(lines) < 2:
            print("  No data returned")
            return False
        header = lines[0]
        data = "\n".join(lines[1:])
        df = pd.read_csv(StringIO(header + "\n" + data))
        path = os.path.join(RAW_DIR, "malwarebazaar.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to {path}")
        print(f"  Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def download_mishra_sms():
    print("\n=== Mishra SMS Phishing Dataset ===")
    try:
        from datasets import load_dataset
        ds = load_dataset("ealvaradob/phishing-dataset", split="train")
        df = ds.to_pandas()
        path = os.path.join(RAW_DIR, "mishra_sms_phishing.csv")
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to {path}")
        print(f"  Columns: {list(df.columns)}")
        if "LABEL" in df.columns:
            print(f"  Label distribution:\n{df['LABEL'].value_counts().to_string()}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Downloading datasets to", RAW_DIR)
    results = {}
    results["phiusiil"] = download_phiusiil()
    results["urlhaus"] = download_urlhaus()
    results["sms_spam"] = download_sms_spam()
    results["malwarebazaar"] = download_malwarebazaar()
    results["mishra_sms"] = download_mishra_sms()

    print("\n=== Summary ===")
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  {name}: {status}")
