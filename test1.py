import subprocess
import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
from fetch_names import search_anime, BASE_URL
from fetch_eps import choose_episode
from m3u8_extractor import extract_m3u8_links


def play_mpv(url):
    subprocess.run(["mpv", url])


def main():
    keyword = input("Search anime or paste link: ").strip()

    # -----------------------------
    # PRIORITY 1: morning-credit / direct links
    # -----------------------------
    if keyword.startswith("https://morning-credit") or "m3u8" in keyword:
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
        headless=False
    )

    if not links:
        print("No stream found.")
        return

    # prefer master.m3u8
    stream = next((l for l in links if "master.m3u8" in l), links[0])

    print("\nPlaying:")
    print(stream)

    play_mpv(stream)


if __name__ == "__main__":
    main()
