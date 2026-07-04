import re
import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

M3U8_PATTERN = re.compile(r"\.m3u8(\?.*)?$", re.I)

# Matches hosts like: morning-credit-3bcc.vibevibe.workers.dev
MORNING_CREDIT_HOST_PATTERN = re.compile(r"^morning-credit[\w.-]*$", re.I)


def is_m3u8_url(url: str) -> bool:
    return bool(
        M3U8_PATTERN.search(urlparse(url).path)
        or M3U8_PATTERN.search(url)
    )


def is_target_stream_url(url: str) -> bool:
    """
    Only accept URLs whose host starts with 'morning-credit' and whose
    path ends in '.m3u8'. e.g.
    https://morning-credit-3bcc.vibevibe.workers.dev/.../master.m3u8
    """
    parsed = urlparse(url)
    host = parsed.netloc.split(":")[0]  # strip port if present
    return bool(
        MORNING_CREDIT_HOST_PATTERN.match(host)
        and M3U8_PATTERN.search(parsed.path)
    )


def click_hd2_safe(locator, max_clicks: int = 5, wait_after_click: float = 1.0):
    """
    Safe HD-2 click with retries:
    - clicks up to `max_clicks` times
    - stops early if already active
    - waits for the click to "settle" between attempts
    - re-fetches the locator's attributes each time in case the DOM changed
    """
    for attempt in range(max_clicks):
        try:
            classes = locator.get_attribute("class") or ""
            if "active" in classes:
                print(f"[HD-2] Already active after {attempt} click(s).")
                return

            try:
                locator.click(timeout=1000)
            except Exception:
                try:
                    locator.click(force=True)
                except Exception:
                    locator.evaluate("el => el.click()")

            print(f"[HD-2] Click attempt {attempt + 1}/{max_clicks}")
            time.sleep(wait_after_click)

        except Exception as e:
            print(f"[HD-2] Click attempt {attempt + 1} failed: {e}")
            break


def wait_for_full_load(page, timeout: int = 15000):
    """
    Waits for the page to be fully loaded/settled after a navigation
    or reload. Falls back gracefully if 'networkidle' never fires
    (common on pages with persistent polling/ads).
    """
    try:
        page.wait_for_load_state("load", timeout=timeout)
    except Exception:
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        # Some streaming sites never go fully idle (ads, pings, etc.)
        pass


def click_hd2_after_each_refresh(page, refresh_rounds: int = 3, clicks_per_round: int = 2):
    """
    Repeats: wait for full page load -> click HD-2 (multiple times) -> optional reload.
    Use this when the button needs to be re-clicked after the page reloads/refreshes,
    e.g. because the server switch triggers a full page reload rather than an in-place swap.
    """
    for round_num in range(refresh_rounds):
        print(f"\n=== Refresh round {round_num + 1}/{refresh_rounds} ===")

        # Make sure the page has fully settled before interacting
        wait_for_full_load(page)

        try:
            btn = page.locator(
                "button.nv-server-btn.server-video"
            ).filter(has_text="HD-2").first
            btn.wait_for(state="visible", timeout=5000)
            btn.scroll_into_view_if_needed()
        except Exception:
            print("[HD-2] Button not found/visible this round.")
            continue

        click_hd2_safe(btn, max_clicks=clicks_per_round)

        # If clicking HD-2 caused a navigation/reload, wait for it to settle
        # before the next round (harmless no-op if nothing happened).
        wait_for_full_load(page)


def extract_m3u8_links(
    page_url: str,
    wait_seconds: int = 5,
    headless: bool = True,
    refresh_rounds: int = 1,
    clicks_per_round: int = 2,
) -> list[str]:
    found = []

    def capture(request):
        url = request.url
        if url not in found and is_target_stream_url(url):
            found.append(url)
            print(f"[m3u8] Found: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(user_agent="Mozilla/5.0")
        page.on("request", capture)

        page.goto(page_url, wait_until="domcontentloaded")
        wait_for_full_load(page)

        # -------------------------
        # CLICK HD-2 SAFELY, MULTIPLE TIMES, ACROSS REFRESHES
        # -------------------------
        click_hd2_after_each_refresh(
            page,
            refresh_rounds=refresh_rounds,
            clicks_per_round=clicks_per_round,
        )

        # Stop early once we've already captured a stream
        if found:
            print("[m3u8] Stream already captured, skipping play-button step.")
        else:
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
                except Exception:
                    pass

        # -------------------------
        # WAIT FOR STREAM
        # -------------------------
        page.wait_for_timeout(wait_seconds * 1000)
        browser.close()

    return found


if __name__ == "__main__":
    links = extract_m3u8_links(
        "https://example.com/some-video-page",
        wait_seconds=6,
        headless=True,
        refresh_rounds=2,
        clicks_per_round=2,
    )
    print("\nFinal results:", links)
