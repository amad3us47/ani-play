import subprocess
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

from fetch_names import search_anime, BASE_URL
from fetch_eps import choose_episode
from m3u8_extractor import extract_m3u8_links, is_target_stream_url


def play_mpv(url):
    subprocess.run(["mpv", url])


def main():
    keyword = input("Search anime or paste link: ").strip()

    # -----------------------------
    # PRIORITY 1: morning-credit / direct links
    # -----------------------------
    if is_target_stream_url(keyword):
        print("\nDirect stream detected...")
        play_mpv(keyword)
        return

    # -----------------------------
    # PRIORITY 2: normal anime flow
    # -----------------------------
    anime = search_anime(keyword)
    if not anime:
        print("No anime found.")
        return

    episode = choose_episode(anime)
    if not episode:
        print("No episodes found.")
        return

    episode_url = BASE_URL + episode
    print("\nSelected Episode:")
    print(episode_url)

    print("\nExtracting stream...")
    links = extract_m3u8_links(
        episode_url,
        wait_seconds=5,
        headless=True,
    )

    if not links:
        print("No stream found.")
        return

    # links are already filtered to morning-credit .../*.m3u8 by extract_m3u8_links,
    # but still prefer master.m3u8 if multiple qualities were captured
    stream = next((l for l in links if "master.m3u8" in l), links[0])

    print("\nPlaying:")
    print(stream)
    play_mpv(stream)


if __name__ == "__main__":
    main()
