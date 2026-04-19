import requests
import base64

API = "https://api.allanime.day/api"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://allanime.to",
    "Referer": "https://allanime.to/",
    "User-Agent": "Mozilla/5.0"
}

def decode_source(encoded):
    return base64.b64decode(encoded[::-1]).decode()

def get_stream_urls(show_id, episode):
    query = """
    query ($showId: String!, $episodeString: String!) {
      episode(showId: $showId, episodeString: $episodeString) {
        sourceUrls
      }
    }
    """

    r = requests.post(API, headers=HEADERS, json={
        "query": query,
        "variables": {
            "showId": show_id,
            "episodeString": str(episode)
        }
    })

    data = r.json()

    if "data" not in data or data["data"]["episode"] is None:
        print("Episode not found")
        return {}

    urls = {}
    for src in data["data"]["episode"]["sourceUrls"]:
        urls[src["sourceName"]] = decode_source(src["sourceUrl"])

    return urls


# 🔴 PUT REAL SHOW ID HERE
show_id = "juiz9RT649YaGTaoQ"   # example id
episode = 1

streams = get_stream_urls(show_id, episode)

for name, url in streams.items():
    print(name, "->", url)
