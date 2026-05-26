"""
scrape_playwright.py  —  Direct Playwright scraper (fallback)
Does NOT use TikTokApi. Controls a real browser directly.

How it works:
  1. Opens a visible Chrome browser
  2. You log in to TikTok once — state is saved so you won't need to again
  3. Visits your profile page and reads the embedded JSON data TikTok puts
     in every page (the __UNIVERSAL_DATA_FOR_REHYDRATION__ script tag)
  4. For each video, visits the video page and collects comments the same way
  5. Saves everything to CSV

Run with:
    python scrape_playwright.py
"""

import asyncio
import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

import config

# ── Output paths ──────────────────────────────────────────────────────────────
Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
stamp         = datetime.now().strftime("%Y%m%d_%H%M%S")
VIDEOS_PATH   = os.path.join(config.OUTPUT_DIR, f"videos_{stamp}.csv")
COMMENTS_PATH = os.path.join(config.OUTPUT_DIR, f"comments_{stamp}.csv")

# Saved browser login state — reused on every run after the first
BROWSER_STATE = "./browser_state.json"

VIDEO_COLS = [
    "video_id", "description", "view_count", "like_count",
    "comment_count", "share_count", "upload_date", "hashtags", "url", "scraped_at",
]
COMMENT_COLS = [
    "comment_id", "video_id", "comment_text", "like_count",
    "author_username", "comment_date", "scraped_at",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def append_csv(rows, filepath, columns):
    if not rows:
        return
    write_header = not Path(filepath).exists()
    with open(filepath, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerows(rows)


def extract_page_data(raw_json: str) -> dict:
    """
    TikTok embeds all page data as JSON in a <script> tag.
    This function parses it and returns the dict.
    """
    try:
        return json.loads(raw_json)
    except Exception:
        return {}


# ── Browser setup ─────────────────────────────────────────────────────────────

async def get_browser_context(playwright):
    """
    Launch a visible Chromium browser.
    Loads saved login state from browser_state.json if it exists.
    """
    browser = await playwright.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )

    if Path(BROWSER_STATE).exists():
        context = await browser.new_context(storage_state=BROWSER_STATE)
        print("Loaded saved login state from browser_state.json")
    else:
        context = await browser.new_context()
        print("No saved login state — will ask you to log in.")

    # Block images and fonts to load pages faster
    await context.route("**/*.{png,jpg,jpeg,gif,webp,woff,woff2}", lambda r: r.abort())

    return browser, context


async def ensure_logged_in(context) -> bool:
    """
    Open TikTok and check if already logged in.
    If not, ask the user to log in manually.
    Saves the session afterwards.
    """
    page = await context.new_page()
    await page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    # Check for login indicator (the upload button only appears when logged in)
    logged_in = await page.query_selector('[data-e2e="upload-icon"]') is not None

    if not logged_in:
        print()
        print("=" * 60)
        print("  Please log in to TikTok in the browser window.")
        print("  Waiting up to 2 minutes for you to log in...")
        print("=" * 60)
        # Wait up to 120 seconds for the feed or profile icon to appear
        try:
            await page.wait_for_selector(
                '[data-e2e="upload-icon"], [data-e2e="nav-avatar"]',
                timeout=120_000
            )
            print("Login detected — continuing.")
        except Exception:
            print("Timed out waiting for login. Trying to continue anyway...")

    # Save the session so we don't need to log in again
    await context.storage_state(path=BROWSER_STATE)
    print("Login state saved to browser_state.json")
    await page.close()
    return True


# ── Video collection ──────────────────────────────────────────────────────────

async def get_videos(context) -> list:
    """
    Visit the profile page and extract video data from the embedded JSON.
    Returns a list of video dicts.
    """
    profile_url = f"https://www.tiktok.com/@{config.TIKTOK_USERNAME}"
    page        = await context.new_page()

    print(f"Opening profile: {profile_url}")
    await page.goto(profile_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    # TikTok stores page data in this script tag
    raw = await page.evaluate("""() => {
        const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
        return el ? el.textContent : null;
    }""")

    videos = []

    if raw:
        data = extract_page_data(raw)
        # Navigate the nested JSON to find the video list
        try:
            items = (
                data
                .get("__DEFAULT_SCOPE__", {})
                .get("webapp.user-detail", {})
                .get("userInfo", {})
            )
            # Video list is usually under a different key — try both paths
            video_list = (
                data
                .get("__DEFAULT_SCOPE__", {})
                .get("webapp.video-list", {})
                .get("itemList", [])
            )
            if not video_list:
                # Try alternate path
                video_list = (
                    data
                    .get("__DEFAULT_SCOPE__", {})
                    .get("webapp.user-post", {})
                    .get("itemList", [])
                )
        except Exception:
            video_list = []

        for item in video_list:
            vid_id = str(item.get("id", ""))
            if not vid_id:
                continue
            stats  = item.get("stats", {})
            desc   = item.get("desc", "")
            tags   = json.dumps([t.get("hashtagName", "") for t in item.get("textExtra", [])
                                 if t.get("type") == 1 and t.get("hashtagName")])
            videos.append({
                "video_id":      vid_id,
                "description":   clean(desc),
                "view_count":    stats.get("playCount", 0),
                "like_count":    stats.get("diggCount", 0),
                "comment_count": stats.get("commentCount", 0),
                "share_count":   stats.get("shareCount", 0),
                "upload_date":   unix_to_iso(item.get("createTime")),
                "hashtags":      tags,
                "url":           f"https://www.tiktok.com/@{config.TIKTOK_USERNAME}/video/{vid_id}",
                "scraped_at":    datetime.now(tz=timezone.utc).isoformat(),
            })

    # If JSON extraction gave nothing, fall back to scraping video links from DOM
    if not videos:
        print("JSON extraction found no videos — falling back to link scraping...")
        videos = await _scrape_video_links(page)

    await page.close()
    print(f"Found {len(videos)} video(s).")
    return videos


async def _scrape_video_links(page) -> list:
    """
    Fallback: scroll the profile page and collect video URLs from <a> tags.
    Returns minimal video dicts (just video_id and url — no stats).
    """
    seen  = set()
    videos = []

    for _ in range(10):                         # scroll up to 10 times
        links = await page.query_selector_all('a[href*="/video/"]')
        for link in links:
            href = await link.get_attribute("href") or ""
            m    = re.search(r"/video/(\d+)", href)
            if m and m.group(1) not in seen:
                vid_id = m.group(1)
                seen.add(vid_id)
                videos.append({
                    "video_id":    vid_id,
                    "description": "",
                    "view_count":  0, "like_count": 0,
                    "comment_count": 0, "share_count": 0,
                    "upload_date": "", "hashtags": "[]",
                    "url": f"https://www.tiktok.com/@{config.TIKTOK_USERNAME}/video/{vid_id}",
                    "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
                })

        await page.keyboard.press("End")
        await page.wait_for_timeout(2000)

    return videos


# ── Comment collection ────────────────────────────────────────────────────────

async def get_comments(context, video_id: str, video_url: str) -> list:
    """
    Intercept the TikTok comments API response directly.

    When you open a TikTok video page, the browser makes a background request to:
      https://www.tiktok.com/api/comment/list/?aweme_id=VIDEO_ID&...
    We listen for that response and parse the JSON it returns.
    This is more reliable than scraping the DOM.
    """
    page     = await context.new_page()
    comments = []
    captured = []   # will hold raw API response dicts

    async def handle_response(response):
        """Called automatically whenever the page receives any network response."""
        if "api/comment/list" in response.url:
            try:
                body = await response.json()
                captured.append(body)
            except Exception:
                pass

    page.on("response", handle_response)

    await page.goto(video_url, wait_until="domcontentloaded")

    # Wait long enough for the comments API call to complete
    await page.wait_for_timeout(5000)

    # Scroll the comments panel to trigger loading more comments
    for _ in range(3):
        await page.keyboard.press("End")
        await page.wait_for_timeout(2000)

    await page.close()

    # Parse all captured API responses
    now = datetime.now(tz=timezone.utc).isoformat()
    for body in captured:
        for c in body.get("comments", []):
            user = c.get("user", {})
            cid  = str(c.get("cid", ""))
            text = clean(c.get("text", ""))
            if not text:
                continue
            comments.append({
                "comment_id":      cid,
                "video_id":        video_id,
                "comment_text":    text,
                "like_count":      c.get("digg_count", 0),
                "author_username": user.get("unique_id", user.get("uniqueId", "")),
                "comment_date":    unix_to_iso(c.get("create_time", c.get("createTime"))),
                "scraped_at":      now,
            })

    if not comments:
        # Final fallback: read comment text from DOM
        comments = await _scrape_comments_dom_reopen(context, video_id, video_url)

    return comments


async def _scrape_comments_dom_reopen(context, video_id: str, video_url: str) -> list:
    """Last-resort fallback: re-open the page and read comment text from DOM."""
    page     = await context.new_page()
    comments = []

    await page.goto(video_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)

    for _ in range(4):
        await page.keyboard.press("End")
        await page.wait_for_timeout(1500)

    # Try every known TikTok comment selector
    for selector in [
        '[data-e2e="comment-level-1"]',
        '[class*="CommentItemWrapper"]',
        '[class*="comment-item"]',
    ]:
        els = await page.query_selector_all(selector)
        if not els:
            continue
        for i, el in enumerate(els):
            try:
                text = (await el.inner_text()).strip()
                first_line = text.split("\n")[0].strip()
                if len(first_line) > 2:
                    comments.append({
                        "comment_id":      f"{video_id}_{i}",
                        "video_id":        video_id,
                        "comment_text":    clean(first_line),
                        "like_count":      0,
                        "author_username": "",
                        "comment_date":    "",
                        "scraped_at":      datetime.now(tz=timezone.utc).isoformat(),
                    })
            except Exception:
                continue
        if comments:
            break

    await page.close()
    return comments


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    stats = {"videos": 0, "comments": 0, "failures": 0}

    async with async_playwright() as p:
        browser, context = await get_browser_context(p)

        try:
            await ensure_logged_in(context)

            # 1 — Get all videos
            videos = await get_videos(context)
            if not videos:
                print("No videos found. Make sure your profile is public.")
                return

            total = len(videos)

            # 2 — For each video, get comments
            for i, video in enumerate(videos, 1):
                vid_id = video["video_id"]
                print(f"[{i}/{total}] Processing video {vid_id} ...")

                try:
                    append_csv([video], VIDEOS_PATH, VIDEO_COLS)
                    stats["videos"] += 1

                    coms = await get_comments(context, vid_id, video["url"])
                    append_csv(coms, COMMENTS_PATH, COMMENT_COLS)
                    stats["comments"] += len(coms)

                    print(f"  → {len(coms)} comment(s) saved")

                except Exception as e:
                    print(f"  ERROR: {e}")
                    stats["failures"] += 1

                await asyncio.sleep(config.DELAY_BETWEEN_VIDEOS)

        finally:
            await context.storage_state(path=BROWSER_STATE)
            await browser.close()

    print()
    print("=" * 60)
    print(f"  Videos   : {stats['videos']}")
    print(f"  Comments : {stats['comments']}")
    print(f"  Failures : {stats['failures']}")
    print(f"  Videos CSV   : {VIDEOS_PATH}")
    print(f"  Comments CSV : {COMMENTS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
