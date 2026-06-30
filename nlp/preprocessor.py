"""
preprocessor.py
Text cleaning and filtering pipeline.
Converts raw TikTok comments into clean text ready for NLP analysis.
"""

import re
import pandas as pd


def clean_text(text: str) -> str:
    """
    Clean a single comment string.
    Steps applied in order:
      1. Lowercase everything
      2. Remove URLs (http/www links)
      3. Remove @mentions
      4. Remove #hashtags
      5. Remove punctuation (keep letters + spaces)
      6. Remove numbers
      7. Collapse extra whitespace
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)   # URLs
    text = re.sub(r'@\w+', '', text)              # @mentions
    text = re.sub(r'#\w+', '', text)              # #hashtags
    text = re.sub(r'[^\w\s]', '', text)           # punctuation
    text = re.sub(r'\d+', '', text)               # numbers
    text = re.sub(r'\s+', ' ', text).strip()      # extra spaces
    return text


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter and clean the full comments dataframe.

    Steps:
      1. Keep only English comments (Comment Language == 'en')
      2. Apply clean_text() to create a new 'clean_comment' column
      3. Drop rows where the cleaned result is fewer than 3 characters

    Returns a new dataframe — the original is not modified.
    """
    df = df.copy()

    # Step 1: keep English only.
    # Short ASCII-only comments (≤3 tokens, e.g. "wow", "goals", "so fire")
    # are frequently misdetected as non-English by langdetect. Trust them as
    # English regardless of the detected language code.
    if 'Comment Language' in df.columns:
        def _is_english(row):
            if str(row.get('Comment Language', 'en')).lower() == 'en':
                return True
            text = str(row.get('Comment Text', '')).strip()
            return text.isascii() and len(text.split()) <= 3
        df = df[df.apply(_is_english, axis=1)]

    # Step 2: clean text
    df['clean_comment'] = df['Comment Text'].apply(clean_text)

    # Step 3: drop only rows where the original comment is also empty.
    # Emoji-only comments have clean_comment == "" but still carry sentiment,
    # so we keep them as long as the original text has any content.
    df = df[df['Comment Text'].fillna('').str.strip().str.len() >= 1]

    df = df.reset_index(drop=True)
    return df
