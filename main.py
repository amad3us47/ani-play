from fetch_names import search_anime, BASE_URL
from fetch_eps import choose_episode


def main():
    keyword = input("Search anime: ").strip()

    anime = search_anime(keyword)
    if not anime:
        print("No anime found.")
        return

    episode = choose_episode(anime)
    if not episode:
        print("No episodes found.")
        return

    print("\nSelected Episode:")
    print(BASE_URL + episode)


if __name__ == "__main__":
    main()
