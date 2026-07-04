import re
import requests
from InquirerPy import inquirer

BASE_URL = "https://anineko.to"


def get_episode_links(watch_path):
    html = requests.get(
        BASE_URL + watch_path,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    ).text

    return sorted(
        set(re.findall(r'/watch/[^"\'>\s]+/ep-\d+(?:\.\d+)?', html)),
        key=lambda x: float(re.search(r'ep-(\d+(?:\.\d+)?)', x).group(1)),
    )


def select_episode(episodes):
    return inquirer.select(
        message="Select episode:",
        choices=episodes,
        height="20",
        cycle=False,
    ).execute()


def choose_episode(watch_path):
    episodes = get_episode_links(watch_path)
    if not episodes:
        return None
    return select_episode(episodes)
