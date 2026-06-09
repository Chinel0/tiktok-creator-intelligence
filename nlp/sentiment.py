"""
sentiment.py
Sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).
VADER is designed specifically for social media text — it understands
slang, emoji, capitalisation, and punctuation patterns.
"""

import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER word list on first use (silent, no output shown)
nltk.download('vader_lexicon', quiet=True)


def _classify(text: str, sia: SentimentIntensityAnalyzer) -> tuple:
    """
    Classify a single comment as positive / negative / neutral.

    VADER returns a compound score in [-1, +1]:
      compound >= +0.05  → positive
      compound <= -0.05  → negative
      in between         → neutral

    Returns (label_string, compound_score).
    """
    if not text or not isinstance(text, str):
        return 'neutral', 0.0

    compound = sia.polarity_scores(text)['compound']

    if compound >= 0.05:
        return 'positive', compound
    elif compound <= -0.05:
        return 'negative', compound
    else:
        return 'neutral', compound


def analyze_sentiment(df: pd.DataFrame) -> tuple:
    """
    Add sentiment columns to the dataframe and return summary statistics.

    New columns added:
      'sentiment'       — 'positive', 'negative', or 'neutral'
      'sentiment_score' — VADER compound score in [-1, +1]

    Returns:
      (enriched_df, summary_dict)

    summary_dict keys:
      total, positive (%), negative (%), neutral (%)
    """
    sia = SentimentIntensityAnalyzer()
    df  = df.copy()

    # Use original text so VADER can read emojis, capitalisation, and punctuation.
    # clean_comment is kept for TF-IDF keyword extraction only.
    text_col = 'Comment Text' if 'Comment Text' in df.columns else 'clean_comment'
    results = df[text_col].apply(lambda t: _classify(t, sia))
    df['sentiment']       = results.apply(lambda x: x[0])
    df['sentiment_score'] = results.apply(lambda x: x[1])

    total = max(len(df), 1)   # guard against empty dataframe
    pos   = (df['sentiment'] == 'positive').sum()
    neg   = (df['sentiment'] == 'negative').sum()
    neu   = (df['sentiment'] == 'neutral').sum()

    summary = {
        'total':    int(total),
        'positive': round(pos / total * 100, 1),
        'negative': round(neg / total * 100, 1),
        'neutral':  round(neu / total * 100, 1),
    }

    return df, summary
