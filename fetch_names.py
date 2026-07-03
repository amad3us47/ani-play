import re
import requests
from InquirerPy import inquirer

BASE_URL = "https://anineko.to"


def get_watch_links(keyword):
    html = requests.get(
        f"{BASE_URL}/browser?keyword={keyword}",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    ).text

    return sorted(set(re.findall(r'/watch/[^"\'>\s]+', html)))


def select_watch_link(links):
    return inquirer.select(
        message="Select anime:",
        choices=links,
        height="20",
        cycle=False,
    ).execute()


def search_anime(keyword):
    links = get_watch_links(keyword)
    if not links:
        return None
    return select_watch_link(links)
