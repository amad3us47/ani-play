from fetch_names import search_anime, BASE_URL
from fetch_eps import choose_episode
from m3u8_extractor import extract_m3u8_links


def main():
    # 1. SEARCH ANIME
    keyword = input("Search anime: ").strip()

    anime = search_anime(keyword)
    if not anime:
        print("No anime found.")
        return

    # 2. SELECT EPISODE
    episode = choose_episode(anime)
    if not episode:
        print("No episodes found.")
        return

    episode_url = BASE_URL + episode

    print("\nSelected Episode:")
    print(episode_url)

    # 3. EXTRACT M3U8 STREAM
    print("\nFetching stream...")

    links = extract_m3u8_links(
        episode_url,
        wait_seconds=15,
        headless=False
    )

    # 4. OUTPUT RESULT
    if links:
        print(f"\nFound {len(links)} stream link(s):\n")
        for link in links:
            print(link)
    else:
        print("\nNo .m3u8 links found.")


if __name__ == "__main__":
    main()
