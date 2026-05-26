# ── config.py ─────────────────────────────────────────────────────────────────
# Shared configuration for both the scraper (scrape.py) and the Streamlit app.
# Edit the values here — no other files need to change.

# ── App settings ──────────────────────────────────────────────────────────────
APP_TITLE    = "TikTok Creator Intelligence"
SAMPLE_DATA  = "./data/raw/sample_comments.csv"
DATABASE     = "./data/tiktok_intelligence.db"

# Your TikTok username (no @)
TIKTOK_USERNAME = "ichbinnelo"

# ── Timing ────────────────────────────────────────────────────────────────────
# Seconds to wait between processing each video (avoids rate limiting)
DELAY_BETWEEN_VIDEOS = 2.5

# Seconds to wait between comment pagination calls for a single video
DELAY_BETWEEN_COMMENT_PAGES = 1.0

# How long to wait (in seconds) after each retry attempt: 30s → 60s → 120s
BACKOFF_SECONDS = [30, 60, 120]

# Stop the whole run if this many videos fail back-to-back
MAX_CONSECUTIVE_FAILURES = 3

# ── Data limits ───────────────────────────────────────────────────────────────
# Maximum comments to collect per video.  Set to None to collect all of them.
MAX_COMMENTS_PER_VIDEO = None

# ── File paths ────────────────────────────────────────────────────────────────
OUTPUT_DIR   = "./data"         # Where videos.csv and comments.csv are written
SESSION_FILE = "./session.json" # Stores the msToken so you don't log in every time
ERRORS_LOG   = "./errors.log"   # Append-mode log for failures
