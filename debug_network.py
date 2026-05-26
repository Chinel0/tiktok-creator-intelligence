"""
debug_network.py
Opens one TikTok video and logs every network request URL.
This tells us the exact URL TikTok uses for the comments API.
Run once, then we update collect_comments.py with the correct URL.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BROWSER_STATE = "./browser_state.json"
# Use the first video URL from the scraped list
TEST_URL = "https://www.tiktok.com/@ichbinnelo/video/7638339125430586657"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        if Path(BROWSER_STATE).exists():
            context = await browser.new_context(storage_state=BROWSER_STATE)
        else:
            context = await browser.new_context()

        page = await context.new_page()
        captured_urls = []

        # Log every network response
        async def on_response(response):
            url = response.url
            # Only log TikTok API calls (skip images, fonts, tracking)
            if "tiktok.com" in url and any(x in url for x in [
                "api", "comment", "aweme", "item", "video"
            ]):
                status = response.status
                captured_urls.append(url)
                print(f"  [{status}] {url[:120]}")

        page.on("response", on_response)

        print(f"Opening: {TEST_URL}")
        print("All TikTok API calls will be logged below:\n")

        await page.goto(TEST_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Scroll to trigger comment loading
        print("\n--- Scrolling to trigger comments ---")
        for _ in range(4):
            await page.keyboard.press("End")
            await page.wait_for_timeout(2000)

        # Try clicking the comments area
        print("\n--- Trying to click comments section ---")
        try:
            comment_btn = await page.query_selector('[data-e2e="comment-icon"]')
            if comment_btn:
                await comment_btn.click()
                print("Clicked comment icon")
                await page.wait_for_timeout(3000)
        except Exception:
            pass

        await page.wait_for_timeout(3000)

        print("\n\n=== ALL CAPTURED URLS ===")
        for url in captured_urls:
            print(url)

        print(f"\nTotal API calls captured: {len(captured_urls)}")

        # Look specifically for comment-related URLs
        comment_urls = [u for u in captured_urls if "comment" in u.lower()]
        print(f"\n=== COMMENT-RELATED URLS ({len(comment_urls)}) ===")
        for url in comment_urls:
            print(url)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
