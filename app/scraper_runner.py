"""
scraper_runner.py
Runs collect_comments.py as a background subprocess and streams
its progress line by line. Used by the Upload page's Connect TikTok tab.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT         = Path(__file__).parent.parent
SCRAPER_PATH = ROOT / "collect_comments.py"
BROWSER_STATE = ROOT / "browser_state.json"
DATA_DIR     = ROOT / "data"

MODES = {
    "Quick  — last 20 videos  (~8 min)":    20,
    "Standard — last 50 videos (~20 min)":  50,
    "Full — all videos         (~55 min)":  None,
}


def session_saved() -> bool:
    """True if a saved TikTok login session exists."""
    return BROWSER_STATE.exists()


def latest_comments_csv() -> Path | None:
    """Return the most recently created comments CSV, or None."""
    files = sorted(DATA_DIR.glob("comments_*.csv"), reverse=True)
    return files[0] if files else None


def run_scraper(limit: int | None):
    """
    Generator that launches the scraper subprocess and yields
    (progress_float_or_None, message_string) tuples as output arrives.
    progress_float is in [0, 1] when a [current/total] line is detected,
    otherwise None (for status messages).
    Yields ("done", csv_path) as the final item when complete.
    """
    cmd = [sys.executable, str(SCRAPER_PATH)]
    if limit:
        cmd += ["--limit", str(limit)]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(ROOT),
        encoding="utf-8",
        errors="replace",
    )

    for raw_line in proc.stdout:
        line = raw_line.strip()
        if not line:
            continue

        # Parse [current/total] progress lines
        m = re.match(r"\[(\d+)/(\d+)\]", line)
        if m:
            current = int(m.group(1))
            total   = int(m.group(2))
            yield current / total, line
        else:
            yield None, line

    proc.wait()

    csv_path = latest_comments_csv()
    yield "done", str(csv_path) if csv_path else ""
