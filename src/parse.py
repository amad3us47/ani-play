import requests
import json

url = "https://api.allanime.day/api"

headers = {
    "Content-Type": "application/json",
    "Origin": "https://allanime.to",
    "Referer": "https://allanime.to/",
    "User-Agent": "Mozilla/5.0"
}

payload = {
    "query": """
    query ($search: SearchInput) {
      shows(search: $search) {
        edges {
          _id
          name
          englishName
          thumbnail
          availableEpisodesDetail
        }
      }
    }
    """,
    "variables": {
        "search": {
            "query": "silent voice"
        }
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print(json.dumps(data, indent=2))
