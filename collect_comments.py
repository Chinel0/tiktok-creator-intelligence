"""
collect_comments.py
Reads the existing videos CSV, visits each video URL in a real browser,
intercepts TikTok's comments API response, and saves all comments to CSV.
Run after scrape_playwright.py has already collected the video list.
"""

import asyncio
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

import config

BROWSER_STATE = "./browser_state.json"
OUTPUT_DIR    = config.OUTPUT_DIR
COMMENT_COLS  = [
    "comment_id", "video_id", "comment_text", "like_count",
    "author_username", "comment_date", "scraped_at",
]


def unix_to_iso(ts):
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return str(ts)


def clean(text):
    if not text:
        return ""
    return re.sub(r"[\n\r\t]+", " ", str(text)).strip()


def append_csv(rows, filepath):
    if not rows:
        return
    write_header = not Path(filepath).exists()
    with open(filepath, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COMMENT_COLS, extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerows(rows)


def find_latest_videos_csv() -> str | None:
    """Return the path of the most recently created videos_*.csv in data/."""
    files = sorted(Path(OUTPUT_DIR).glob("videos_*.csv"), reverse=True)
    return str(files[0]) if files else None


def load_video_urls(videos_csv: str) -> list:
    """Read video_id and url from the videos CSV."""
    rows = []
    with open(videos_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            vid_id = row.get("video_id", "").strip()
            url    = row.get("url", "").strip()
            if vid_id and url:
                rows.append({"video_id": vid_id, "url": url})
    return rows


async def collect_comments_for_video(context, video_id: str, url: str) -> list:
    """
    Open one video page, intercept the /api/comment/list/ network call,
    and return a list of comment dicts.
    """
    page     = await context.new_page()
    captured = []

    async def on_response(response):
        if "api/comment/list" in response.url:
            try:
                body = await response.json()
                captured.append(body)
            except Exception:
                pass

    page.on("response", on_response)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(3000)
        # Must click the comment icon to trigger the comments API call
        try:
            await page.click('[data-e2e="comment-icon"]', timeout=5000)
            await page.wait_for_timeout(3000)
        except Exception:
            pass
        # Scroll to load more comments
        for _ in range(3):
            await page.keyboard.press("End")
            await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"  Page load error: {e}")
    finally:
        await page.close()

    # Parse captured API responses
    comments = []
    now      = datetime.now(tz=timezone.utc).isoformat()
    for body in captured:
        for c in body.get("comments") or []:
            user = c.get("user", {})
            text = clean(c.get("text", ""))
            if not text:
                continue
            comments.append({
                "comment_id":      str(c.get("cid", "")),
                "video_id":        video_id,
                "comment_text":    text,
                "like_count":      c.get("digg_count", 0),
                "author_username": user.get("unique_id", user.get("uniqueId", "")),
                "comment_date":    unix_to_iso(c.get("create_time") or c.get("createTime")),
                "scraped_at":      now,
            })

    return comments


async def main():
    # Find the most recent videos CSV
    videos_csv = find_latest_videos_csv()
    if not videos_csv:
        print("No videos CSV found in data/. Run scrape_playwright.py first.")
        return

    videos = load_video_urls(videos_csv)
    print(f"Loaded {len(videos)} video URLs from {videos_csv}")

    # Output file
    stamp        = datetime.now().strftime("%Y%m%d_%H%M%S")
    comments_csv = os.path.join(OUTPUT_DIR, f"comments_{stamp}.csv")

    # Check if a comments CSV already exists and skip those video IDs
    done_ids = set()
    existing = sorted(Path(OUTPUT_DIR).glob("comments_*.csv"), reverse=True)
    if existing:
        with open(str(existing[0]), encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                done_ids.add(row.get("video_id", "").strip())
        if done_ids:
            comments_csv = str(existing[0])   # append to existing file
            print(f"Resuming: {len(done_ids)} videos already have comments.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )

        # Load saved login — no manual login needed
        if Path(BROWSER_STATE).exists():
            context = await browser.new_context(storage_state=BROWSER_STATE)
            print("Loaded saved login state.")
        else:
            print("No saved login. Please log in when the browser opens.")
            context = await browser.new_context()

        total_comments = 0
        total          = len(videos)

        for i, video in enumerate(videos, 1):
            vid_id = video["video_id"]

            if vid_id in done_ids:
                print(f"[{i}/{total}] Skipping {vid_id} (already done)")
                continue

            print(f"[{i}/{total}] {vid_id} ...", end=" ", flush=True)

            try:
                coms = await collect_comments_for_video(context, vid_id, video["url"])
                append_csv(coms, comments_csv)
                total_comments += len(coms)
                print(f"{len(coms)} comments")
            except Exception as e:
                print(f"ERROR: {e}")

            await asyncio.sleep(config.DELAY_BETWEEN_VIDEOS)

        await context.storage_state(path=BROWSER_STATE)
        await browser.close()

    print()
    print("=" * 50)
    print(f"  Total comments saved : {total_comments}")
    print(f"  Comments CSV         : {comments_csv}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
