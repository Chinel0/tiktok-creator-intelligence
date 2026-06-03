"""
walking_skeleton.py
Proves the full pipeline works end to end.
Raw CSV  →  Preprocessor  →  Sentiment  →  Keywords  →  User output
No mocked data. No UI. Every step is real.
"""

import pandas as pd
from pathlib import Path
import sys

# Ensure imports resolve correctly no matter which folder you run from
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from nlp.preprocessor import preprocess
from nlp.sentiment    import analyze_sentiment
from nlp.keywords     import extract_keywords, CLUSTER_LABELS

# ── STEP 1: Load raw scraped data ─────────────────────────────────────────────
print("STEP 1 - Loading raw data...")
df = pd.read_csv(ROOT / "data/comments_20260526_233400.csv", encoding="utf-8-sig")

# Align column names so the NLP modules can read them
df = df.rename(columns={"comment_text": "Comment Text", "language": "Comment Language"})
print(f"         {len(df)} comments loaded from @ichbinnelo")

# ── STEP 2: Preprocess ────────────────────────────────────────────────────────
print("\nSTEP 2 - Preprocessing...")
df_clean = preprocess(df)
print(f"         {len(df_clean)} comments remain after cleaning (English only, no noise)")

# ── STEP 3: Sentiment analysis ────────────────────────────────────────────────
print("\nSTEP 3 - Running sentiment analysis (VADER)...")
df_sentiment, summary = analyze_sentiment(df_clean)
print(f"         Positive : {summary['positive']}%")
print(f"         Neutral  : {summary['neutral']}%")
print(f"         Negative : {summary['negative']}%")

# ── STEP 4: Keyword extraction ────────────────────────────────────────────────
print("\nSTEP 4 - Extracting keywords (TF-IDF)...")
keywords, clusters = extract_keywords(df_sentiment, top_n=10)
print(f"         Top 5 keywords: {[w for w, _ in keywords[:5]]}")

# ── STEP 5: Output reaches the user ───────────────────────────────────────────
print("\n" + "=" * 50)
print("  ANALYSIS COMPLETE")
print("=" * 50)
print(f"  Comments analysed : {summary['total']}")
print(f"  Audience mood     : {summary['positive']}% positive")
print(f"  Top keyword       : {keywords[0][0] if keywords else 'n/a'}")
print()
print("  Keyword clusters:")
for cluster, words in clusters.items():
    if words:
        label = CLUSTER_LABELS[cluster]
        print(f"    {label:<25} : {', '.join(words[:3])}")
print("=" * 50)
