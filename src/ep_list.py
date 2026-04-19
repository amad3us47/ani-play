import requests

API = "https://api.allanime.day/api"
REFERER = "https://allmanga.to"

HEADERS = {
    "Referer": REFERER,
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

def get_episode_list(show_id, mode="sub"):
    """
    show_id : anime id from search
    mode    : 'sub' or 'dub'
    """

    query = """
    query ($showId: String!) {
        show(_id: $showId) {
            _id
            availableEpisodesDetail
        }
    }
    """

    payload = {
        "variables": {"showId": show_id},
        "query": query
    }

    r = requests.post(API, json=payload, headers=HEADERS)
    data = r.json()

    # Extract episode list
    episodes_data = data["data"]["show"]["availableEpisodesDetail"]

    # Choose sub or dub
    episode_list = episodes_data.get(mode, [])

    # Convert to sorted list of strings
    episode_list = sorted([str(ep) for ep in episode_list], key=lambda x: float(x))

    return episode_list

"""

# 🔎 Example usage
if __name__ == "__main__":
    show_id = "naruto-id-here"  # <- from search API
    eps = get_episode_list(show_id)

    print(f"Total episodes: {len(eps)}")
    print("First 10 episodes:", eps[:10])
"""
