#!/usr/bin/env python3
"""Translate English scam messages to Khmer using MyMemory API.
Run in background: screen -dmS translate python3 translate_to_km.py
"""
import pandas as pd
import time
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

OUTPUT_FILE = "data/raw/khmer_translated.csv"
BATCH_SIZE = 50
DELAY_BETWEEN = 1.5  # seconds between requests
DELAY_AFTER_BATCH = 30  # seconds after each batch

def translate_batch(texts, translator):
    results = []
    for text in texts:
        try:
            r = translator.translate(str(text)[:400])
            if r:
                results.append(r)
            else:
                results.append(None)
        except Exception as e:
            if "429" in str(e) or "Too Many" in str(e):
                print(f"  Rate limited, sleeping 60s...")
                time.sleep(60)
                try:
                    r = translator.translate(str(text)[:400])
                    results.append(r if r else None)
                except:
                    results.append(None)
            else:
                results.append(None)
        time.sleep(DELAY_BETWEEN)
    return results

def main():
    from deep_translator import MyMemoryTranslator
    
    df = pd.read_csv("data/raw/combined_spam_ham.csv", encoding="utf-8")
    
    # Load existing translations
    if os.path.exists(OUTPUT_FILE):
        done_df = pd.read_csv(OUTPUT_FILE, encoding="utf-8")
        done_texts = set(done_df["text"].tolist())
        all_translated = done_df.to_dict("records")
        print(f"Loaded {len(done_texts)} existing translations")
    else:
        done_texts = set()
        all_translated = []
    
    # Get messages to translate
    spam_texts = df[df["label"] == "spam"]["text"].tolist()
    ham_texts = df[df["label"] == "ham"]["text"].tolist()
    
    # Filter out already translated
    spam_todo = [t for t in spam_texts if t not in done_texts][:2000]
    ham_todo = [t for t in ham_texts if t not in done_texts][:2000]
    
    print(f"To translate: {len(spam_todo)} spam + {len(ham_todo)} ham")
    
    translator = MyMemoryTranslator(source="en-GB", target="km-KH")
    
    # Translate spam
    for i in range(0, len(spam_todo), BATCH_SIZE):
        batch = spam_todo[i:i+BATCH_SIZE]
        print(f"Spam batch {i//BATCH_SIZE + 1}: translating {len(batch)}...")
        
        results = translate_batch(batch, translator)
        for text, result in zip(batch, results):
            if result:
                all_translated.append({"text": result, "label": "spam"})
                done_texts.add(text)
        
        # Save after each batch
        pd.DataFrame(all_translated).to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        print(f"  Saved. Total: {len(all_translated)}")
        time.sleep(DELAY_AFTER_BATCH)
    
    # Translate ham
    for i in range(0, len(ham_todo), BATCH_SIZE):
        batch = ham_todo[i:i+BATCH_SIZE]
        print(f"Ham batch {i//BATCH_SIZE + 1}: translating {len(batch)}...")
        
        results = translate_batch(batch, translator)
        for text, result in zip(batch, results):
            if result:
                all_translated.append({"text": result, "label": "ham"})
                done_texts.add(text)
        
        pd.DataFrame(all_translated).to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        print(f"  Saved. Total: {len(all_translated)}")
        time.sleep(DELAY_AFTER_BATCH)
    
    print(f"\nDONE! Total translated: {len(all_translated)}")

if __name__ == "__main__":
    main()
