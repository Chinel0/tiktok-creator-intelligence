#!/usr/bin/env python3
"""
TikTok Creator Intelligence — Data Scraper
Collects all videos and comments from @ichbinnelo and saves them as two CSV
files ready for NLP analysis.

Usage:
    python scrape.py

On first run a browser window will open so you can log in to TikTok.
The session is saved to session.json and reused on subsequent runs.
Videos already in the output CSV are skipped (resume support).
"""

import asyncio
import csv
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from TikTokApi import TikTokApi
from playwright.async_api import async_playwright

import config

# ── Logging ───────────────────────────────────────────────────────────────────
# Writes INFO+ to stdout and ERROR+ to errors.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.ERRORS_LOG, mode="a", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Small utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def ts_now() -> str:
    """Return a filesystem-safe timestamp string, e.g. '20260526_143000'."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def unix_to_iso(ts) -> str:
    """Convert a Unix timestamp (int or str) to an ISO 8601 UTC string."""
    if not ts:
        return ""
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def clean_text(text: str) -> str:
    """Remove newlines and tabs that would corrupt CSV columns."""
    if not text:
        return ""
    return re.sub(r"[\n\r\t]+", " ", text).strip()


def extract_hashtags(text_extra: list) -> str:
    """
    TikTok's textExtra field is a list of annotation objects.
    Pull out entries with type==1 (hashtags) and return as a JSON array string.
    Example output: '["fyp", "cooking", "recipe"]'
    """
    if not text_extra:
        return "[]"
    tags = [
        item.get("hashtagName", "")
        for item in text_extra
        if item.get("type") == 1 and item.get("hashtagName")
    ]
    return json.dumps(tags, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
#  Session management  (save / load msToken so the browser only opens once)
# ─────────────────────────────────────────────────────────────────────────────

def load_session() -> str | None:
    """Return the saved msToken from session.json, or None if absent."""
    path = Path(config.SESSION_FILE)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        token = data.get("ms_token")
        if token:
            log.info("Session loaded from %s", config.SESSION_FILE)
        return token
    except Exception as exc:
        log.warning("Could not load session.json: %s", exc)
        return None


def save_session(ms_token: str) -> None:
    """Persist the msToken to session.json for future runs."""
    payload = {
        "ms_token": ms_token,
        "saved_at": datetime.now(tz=timezone.utc).isoformat(),
        "username": config.TIKTOK_USERNAME,
    }
    Path(config.SESSION_FILE).write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    log.info("Session saved to %s", config.SESSION_FILE)


async def login() -> str:
    """
    Open a visible Playwright browser so you can log in to TikTok manually.
    Once you confirm in the terminal that you are logged in, the msToken cookie
    is extracted from the browser and returned as a string.

    The msToken is the key TikTokApi needs to authenticate its API calls.
    """
    log.info("No saved session found — opening browser for manual TikTok login.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.tiktok.com/login")

        print()
        print("=" * 60)
        print("  A TikTok login page has opened in your browser.")
        print("  Log in with your @ichbinnelo account.")
        print("  After you can see your TikTok feed, come back here")
        print("  and press ENTER to continue.")
        print("=" * 60)
        input("\n  Press ENTER when you are fully logged in... ")

        # TikTok sets the msToken cookie once the session is established.
        cookies = await context.cookies()
        ms_token = next(
            (c["value"] for c in cookies if c.get("name") == "msToken"), None
        )

        await browser.close()

    if not ms_token:
        raise RuntimeError(
            "msToken cookie not found after login.\n"
            "Make sure you are fully logged in and your feed is visible, "
            "then re-run the script."
        )

    log.info("msToken extracted successfully.")
    return ms_token


# ─────────────────────────────────────────────────────────────────────────────
#  Resume support  (skip videos already in the output CSV)
# ─────────────────────────────────────────────────────────────────────────────

def load_scraped_video_ids(filepath: str) -> set:
    """
    Read an existing videos CSV and return the set of video IDs already stored.
    Returns an empty set if the file does not exist yet.
    """
    path = Path(filepath)
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig", usecols=["video_id"], dtype=str)
        ids = set(df["video_id"].dropna().tolist())
        log.info("Resume: %d video IDs already in %s — these will be skipped.", len(ids), filepath)
        return ids
    except Exception as exc:
        log.warning("Could not read existing videos CSV for resume: %s", exc)
        return set()


# ─────────────────────────────────────────────────────────────────────────────
#  Data extraction  (raw API dicts → flat CSV dicts)
# ─────────────────────────────────────────────────────────────────────────────

def extract_video_row(vdict: dict) -> dict:
    """
    Convert a raw TikTok video API dict into a flat row suitable for CSV.
    Uses .get() everywhere so missing fields become empty strings / zeros.
    """
    stats  = vdict.get("stats", {})
    vmeta  = vdict.get("video", {})
    author = vdict.get("author", {})
    vid    = str(vdict.get("id", ""))

    return {
        "video_id":        vid,
        "description":     clean_text(vdict.get("desc", "")),
        "view_count":      stats.get("playCount", 0),
        "like_count":      stats.get("diggCount", 0),
        "comment_count":   stats.get("commentCount", 0),
        "share_count":     stats.get("shareCount", 0),
        "upload_date":     unix_to_iso(vdict.get("createTime")),
        "duration_seconds": vmeta.get("duration", 0),
        "hashtags":        extract_hashtags(vdict.get("textExtra", [])),
        "url":             f"https://www.tiktok.com/@{author.get('uniqueId', config.TIKTOK_USERNAME)}/video/{vid}",
        "scraped_at":      datetime.now(tz=timezone.utc).isoformat(),
    }


def extract_comment_row(cdict: dict, video_id: str) -> dict:
    """
    Convert a raw TikTok comment API dict into a flat row suitable for CSV.
    parent_comment_id is populated for replies; empty for top-level comments.
    """
    user = cdict.get("user", {})

    # TikTok uses replyId / reply_id = "0" for top-level comments
    raw_parent = cdict.get("replyId") or cdict.get("reply_id", "")
    parent_id  = "" if str(raw_parent) in ("0", "") else str(raw_parent)

    return {
        "comment_id":        str(cdict.get("cid", "")),
        "video_id":          str(video_id),
        "comment_text":      clean_text(cdict.get("text", "")),
        "language":          cdict.get("textLanguage", ""),
        "like_count":        cdict.get("diggCount", 0),
        "reply_count":       cdict.get("replyCommentTotal", 0),
        "author_username":   user.get("uniqueId", ""),
        "parent_comment_id": parent_id,
        "comment_date":      unix_to_iso(cdict.get("createTime")),
        "scraped_at":        datetime.now(tz=timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  CSV writers  (append-safe, UTF-8 with BOM so Excel handles emoji correctly)
# ─────────────────────────────────────────────────────────────────────────────

VIDEO_COLUMNS = [
    "video_id", "description", "view_count", "like_count", "comment_count",
    "share_count", "upload_date", "duration_seconds", "hashtags", "url", "scraped_at",
]

COMMENT_COLUMNS = [
    "comment_id", "video_id", "comment_text", "language", "like_count",
    "reply_count", "author_username", "parent_comment_id", "comment_date", "scraped_at",
]


def _append_csv(rows: list[dict], filepath: str, columns: list[str]) -> None:
    """
    Append a list of row dicts to a CSV file.
    Writes the header row only when the file is brand new.
    utf-8-sig encoding adds a BOM so Excel opens the file without garbling emoji.
    """
    if not rows:
        return
    write_header = not Path(filepath).exists()
    with open(filepath, "a", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def save_videos(rows: list[dict], filepath: str) -> None:
    _append_csv(rows, filepath, VIDEO_COLUMNS)
    log.info("  → Saved %d video row(s) to %s", len(rows), filepath)


def save_comments(rows: list[dict], filepath: str) -> None:
    _append_csv(rows, filepath, COMMENT_COLUMNS)
    log.info("  → Saved %d comment row(s) to %s", len(rows), filepath)


# ─────────────────────────────────────────────────────────────────────────────
#  Retry helper  (exponential backoff on transient errors)
# ─────────────────────────────────────────────────────────────────────────────

async def with_backoff(coro_factory, label: str):
    """
    Call an async factory function with retries.
    coro_factory must be a zero-argument callable that returns a coroutine.
    Waits BACKOFF_SECONDS[i] between each attempt; raises after all attempts fail.
    """
    attempts = config.BACKOFF_SECONDS + [None]   # None signals the final attempt
    for i, wait in enumerate(attempts):
        try:
            return await coro_factory()
        except Exception as exc:
            if wait is None:
                log.error("All retries exhausted for '%s': %s", label, exc)
                raise
            log.warning(
                "Attempt %d failed for '%s': %s — retrying in %ds", i + 1, label, exc, wait
            )
            await asyncio.sleep(wait)


# ─────────────────────────────────────────────────────────────────────────────
#  Core scrapers
# ─────────────────────────────────────────────────────────────────────────────

async def get_videos(api: TikTokApi) -> list[dict]:
    """
    Fetch all public videos from TIKTOK_USERNAME.
    Returns a list of raw video dicts from the TikTok API.
    TikTokApi paginates automatically — it keeps requesting until there are
    no more videos to return.
    """
    log.info("Fetching video list for @%s ...", config.TIKTOK_USERNAME)
    user    = api.user(username=config.TIKTOK_USERNAME)
    videos  = []

    async for video in user.videos(count=30):
        videos.append(video.as_dict)

    log.info("Found %d video(s) for @%s.", len(videos), config.TIKTOK_USERNAME)
    return videos


async def get_comments_for_video(api: TikTokApi, video_id: str) -> list[dict]:
    """
    Collect ALL comments (top-level + nested replies) for a single video.

    Strategy:
      1. Iterate top-level comments in pages of 30.
      2. For each comment that has replies (replyCommentTotal > 0), iterate
         its replies too and tag them with the parent comment ID.
      3. Stop early if MAX_COMMENTS_PER_VIDEO is set and reached.
      4. Wait DELAY_BETWEEN_COMMENT_PAGES seconds after each page to be polite.
    """
    comments  = []
    cap       = config.MAX_COMMENTS_PER_VIDEO
    video_obj = api.video(id=video_id)

    async for comment in video_obj.comments(count=30):
        cdict = comment.as_dict
        comments.append(cdict)

        # If this comment has replies, fetch them now
        reply_count = cdict.get("replyCommentTotal", 0)
        if reply_count and reply_count > 0:
            try:
                async for reply in comment.replies(count=30):
                    comments.append(reply.as_dict)
                    if cap and len(comments) >= cap:
                        return comments
                    await asyncio.sleep(0.3)   # small pause between reply pages
            except AttributeError:
                # Some TikTokApi versions don't expose comment.replies() — skip
                pass

        if cap and len(comments) >= cap:
            return comments

        await asyncio.sleep(config.DELAY_BETWEEN_COMMENT_PAGES)

    return comments


# ─────────────────────────────────────────────────────────────────────────────
#  Main orchestration
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    # ── Prepare output directory ─────────────────────────────────────────────
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Output files get a timestamp so each run has a unique name
    stamp        = ts_now()
    videos_path  = os.path.join(config.OUTPUT_DIR, f"videos_{stamp}.csv")
    comments_path = os.path.join(config.OUTPUT_DIR, f"comments_{stamp}.csv")

    # ── Resume: check if a previous run left a videos CSV ───────────────────
    # Scan for the most recent videos_*.csv and, if found, reuse that file pair
    # so we append to it rather than starting a new file.
    existing_ids: set = set()
    for prev_file in sorted(Path(config.OUTPUT_DIR).glob("videos_*.csv"), reverse=True):
        ids = load_scraped_video_ids(str(prev_file))
        if ids:
            existing_ids  = ids
            videos_path   = str(prev_file)
            comments_path = str(prev_file).replace("videos_", "comments_")
            log.info("Resuming: appending to %s", videos_path)
            break

    # ── Session / authentication ─────────────────────────────────────────────
    ms_token = load_session()
    if not ms_token:
        ms_token = await login()
        save_session(ms_token)

    # ── Run stats ────────────────────────────────────────────────────────────
    stats = {"videos_scraped": 0, "comments_collected": 0, "failures": 0}

    # ── TikTokApi scraping ───────────────────────────────────────────────────
    try:
        async with TikTokApi() as api:
            # create_sessions opens a headless browser internally for each token
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                headless=True,
            )

            # 1) Fetch the full video list
            raw_videos = await with_backoff(
                lambda: get_videos(api), "get_videos"
            )
            total = len(raw_videos)

            # 2) Process each video
            consecutive_failures = 0

            for idx, vdict in enumerate(raw_videos, start=1):
                vid = str(vdict.get("id", ""))

                if vid in existing_ids:
                    log.info("[%d/%d] Skipping %s (already scraped)", idx, total, vid)
                    continue

                log.info("[%d/%d] Processing video %s ...", idx, total, vid)

                try:
                    # Save the video row immediately — if comment scraping
                    # crashes, at least the video metadata is not lost.
                    video_row = extract_video_row(vdict)
                    save_videos([video_row], videos_path)
                    stats["videos_scraped"] += 1

                    # Fetch and save comments
                    raw_comments = await with_backoff(
                        lambda: get_comments_for_video(api, vid),
                        f"comments:{vid}",
                    )
                    comment_rows = [extract_comment_row(c, vid) for c in raw_comments]
                    save_comments(comment_rows, comments_path)
                    stats["comments_collected"] += len(comment_rows)

                    log.info(
                        "[%d/%d] Done: %s — %d comment(s)", idx, total, vid, len(comment_rows)
                    )
                    consecutive_failures = 0

                except Exception as exc:
                    log.error("[%d/%d] FAILED video %s: %s", idx, total, vid, exc)
                    stats["failures"] += 1
                    consecutive_failures += 1

                    if consecutive_failures >= config.MAX_CONSECUTIVE_FAILURES:
                        log.error(
                            "Stopping early: %d consecutive failures hit the limit.",
                            consecutive_failures,
                        )
                        break

                # Polite delay between videos to avoid rate limiting
                await asyncio.sleep(config.DELAY_BETWEEN_VIDEOS)

    except Exception as exc:
        log.error("TikTokApi failed with a fatal error: %s", exc)
        print()
        print("=" * 60)
        print("  TikTokApi could not complete the scrape.")
        print()
        print("  Possible reasons:")
        print("    • Your msToken has expired — delete session.json and re-run")
        print("    • TikTok changed their API — check for a TikTokApi update:")
        print("        pip install --upgrade TikTokApi")
        print("    • You have been rate-limited — wait 30 minutes and retry")
        print()
        print("  Fallback option:")
        print("    If TikTokApi is completely broken, run scrape_playwright.py")
        print("    which uses direct browser automation instead.")
        print("=" * 60)
        raise

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  Videos scraped    :  {stats['videos_scraped']}")
    print(f"  Comments collected:  {stats['comments_collected']}")
    print(f"  Failures          :  {stats['failures']}")
    print(f"  Videos CSV        :  {videos_path}")
    print(f"  Comments CSV      :  {comments_path}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
