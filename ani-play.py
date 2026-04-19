from src.parse import fetch_anime

result = fetch_anime("naruto")

edges = result.get("data", {}).get("shows", {}).get("edges", [])

for anime in edges:
    print(anime.get("_id"), "-", anime.get("englishName") or anime.get("name"))
