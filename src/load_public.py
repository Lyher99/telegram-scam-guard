import os
import pandas as pd
import numpy as np

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def load_phiusiil():
    path = os.path.join(RAW_DIR, "phiusiil.csv")
    df = pd.read_csv(path)
    df["label"] = df["label"].map({1: "safe", 0: "dangerous"})
    df = df[["URL", "label"]].copy()
    df.columns = ["text", "label"]
    df["source_dataset"] = "phiusiil"
    df["language"] = "en"
    df["type"] = "url"
    print(f"PhiUSIIL: {len(df)} rows")
    print(f"  Balance: {df['label'].value_counts().to_dict()}")
    return df


def load_urlhaus():
    path = os.path.join(RAW_DIR, "urlhaus.csv")
    df = pd.read_csv(path, header=None, on_bad_lines="skip")
    if len(df.columns) >= 6:
        df = df.iloc[:, [2, 5]].copy()
        df.columns = ["text", "label"]
        df["label"] = df["label"].map(lambda x: "dangerous" if "malware" in str(x).lower() else "suspicious")
    else:
        df = pd.DataFrame(columns=["text", "label"])
    df["source_dataset"] = "urlhaus"
    df["language"] = "en"
    df["type"] = "url"
    print(f"URLhaus: {len(df)} rows")
    print(f"  Balance: {df['label'].value_counts().to_dict()}")
    return df


def load_sms_spam():
    path = os.path.join(RAW_DIR, "sms_spam.csv")
    df = pd.read_csv(path)
    df["label"] = df["label"].map({"ham": "safe", "spam": "suspicious"})
    df = df[["text", "label"]].copy()
    df["source_dataset"] = "sms_spam"
    df["language"] = "en"
    df["type"] = "text"
    print(f"SMS Spam: {len(df)} rows")
    print(f"  Balance: {df['label'].value_counts().to_dict()}")
    return df


def load_malwarebazaar():
    path = os.path.join(RAW_DIR, "malwarebazaar.csv")
    df = pd.read_csv(path, on_bad_lines="skip")
    cols = list(df.columns)
    if len(cols) >= 6:
        name_col = cols[5]
        df = df[[name_col]].copy()
        df.columns = ["text"]
        df["text"] = df["text"].astype(str).str.strip().str.strip('"')
        df = df[df["text"].notna() & (df["text"] != "n/a") & (df["text"] != "")]
        df["label"] = "dangerous"
    else:
        df = pd.DataFrame(columns=["text", "label"])
    df["source_dataset"] = "malwarebazaar"
    df["language"] = "en"
    df["type"] = "file_name"
    print(f"MalwareBazaar: {len(df)} rows")
    return df


def load_all():
    frames = []
    for loader_name in ["load_phiusiil", "load_urlhaus", "load_sms_spam", "load_malwarebazaar"]:
        try:
            fn = globals()[loader_name]
            df = fn()
            if len(df) > 0:
                frames.append(df)
        except Exception as e:
            print(f"  ERROR loading {loader_name}: {e}")

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["split_group"] = combined["source_dataset"]

    print(f"\n=== Combined dataset: {len(combined)} rows ===")
    print(f"By label:\n{combined['label'].value_counts().to_string()}")
    print(f"By source:\n{combined['source_dataset'].value_counts().to_string()}")

    return combined


if __name__ == "__main__":
    df = load_all()
    out = os.path.join(RAW_DIR, "..", "processed", "combined.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved combined dataset to {out}")
