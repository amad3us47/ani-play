import re
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

M3U8_PATTERN = re.compile(r"\.m3u8(\?.*)?$", re.I)


def is_m3u8_url(url: str) -> bool:
    return bool(
        M3U8_PATTERN.search(urlparse(url).path)
        or M3U8_PATTERN.search(url)
    )


def click_hd2_safe(locator):
    """
    Safe HD-2 click:
    - max 2 clicks
    - stops if already active
    - prevents UI misclick issues
    """
    for _ in range(2):
        try:
            classes = locator.get_attribute("class") or ""

            # STOP if already active
            if "active" in classes:
                return

            try:
                locator.click(timeout=1000)
            except:
                try:
                    locator.click(force=True)
                except:
                    locator.evaluate("el => el.click()")

            time.sleep(0.5)

        except:
            break


def extract_m3u8_links(page_url: str, wait_seconds: int = 5, headless: bool = True) -> list[str]:
    found = []

    def capture(request):
        url = request.url
        if url not in found and is_m3u8_url(url):
            found.append(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page(user_agent="Mozilla/5.0")

        page.on("request", capture)

        page.goto(page_url, wait_until="domcontentloaded")

        # -------------------------
        # CLICK HD-2 SAFELY
        # -------------------------
        try:
            btn = page.locator(
                "button.nv-server-btn.server-video"
            ).filter(has_text="HD-2").first

            btn.scroll_into_view_if_needed()
            click_hd2_safe(btn)

        except:
            pass

        # -------------------------
        # PLAY BUTTON CLICK
        # -------------------------
        for sel in [
            ".vjs-big-play-button",
            "video",
            "button[aria-label*='play' i]",
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    el.click(timeout=800)
                    break
            except:
                pass

        # -------------------------
        # WAIT FOR STREAM
        # -------------------------
        page.wait_for_timeout(wait_seconds * 1000)

        browser.close()

    return found
