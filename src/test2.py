import requests, re, json, base64, hashlib, subprocess
from Crypto.Cipher import AES
from Crypto.Util import Counter

API = "https://api.allanime.day/api"
REFERER = "https://allmanga.to"
HEADERS = {"Referer": REFERER, "User-Agent": "Mozilla/5.0"}

# ---------------- SEARCH ----------------

def search_anime(query):
    gql = """
    query($search:SearchInput,$limit:Int,$page:Int,$translationType:VaildTranslationTypeEnumType,$countryOrigin:VaildCountryOriginEnumType){
      shows(search:$search,limit:$limit,page:$page,translationType:$translationType,countryOrigin:$countryOrigin){
        edges{_id name}
      }
    }
    """
    vars = {
        "search":{"allowAdult":False,"allowUnknown":False,"query":query},
        "limit":20,"page":1,"translationType":"sub","countryOrigin":"ALL"
    }

    r = requests.post(API,json={"query":gql,"variables":vars},headers=HEADERS).json()
    data = r["data"]["shows"]["edges"]

    print("\nResults:")
    for i,a in enumerate(data):
        print(f"{i+1}. {a['name']}")

    idx = int(input("\nSelect anime: ")) - 1
    return data[idx]["_id"], data[idx]["name"]

# ---------------- EPISODE LIST ----------------

def get_episode_list(show_id):
    gql = """
    query($showId:String!,$translationType:VaildTranslationTypeEnumType,$countryOrigin:VaildCountryOriginEnumType){
      show(_id:$showId,translationType:$translationType,countryOrigin:$countryOrigin){
        availableEpisodesDetail
      }
    }
    """

    vars = {"showId":show_id,"translationType":"sub","countryOrigin":"ALL"}
    r = requests.post(API,json={"query":gql,"variables":vars},headers=HEADERS).json()
    return r["data"]["show"]["availableEpisodesDetail"]["sub"]

# ---------------- GET EPISODE ID ----------------

def get_episode_id(show_id, ep):
    gql = """
    query($showId:String!,$translationType:VaildTranslationTypeEnumType,$countryOrigin:VaildCountryOriginEnumType){
      show(_id:$showId,translationType:$translationType,countryOrigin:$countryOrigin){
        episodes{
          edges{
            _id
            episodeString
          }
        }
      }
    }
    """

    vars = {"showId":show_id,"translationType":"sub","countryOrigin":"ALL"}
    r = requests.post(API,json={"query":gql,"variables":vars},headers=HEADERS).json()

    if "data" not in r:
        raise Exception("GraphQL error: " + str(r))

    edges = r["data"]["show"]["episodes"]["edges"]
    formats = [ep, ep.zfill(2), ep + ".0", ep.zfill(3)]

    for fmt in formats:
        for e in edges:
            if e["episodeString"] == fmt:
                print("✔ Episode ID found using format:", fmt)
                return e["_id"]

    raise Exception("Episode exists but ID not found.")

# ---------------- GET ENCRYPTED SOURCES ----------------

def get_episode_blob(episode_id):
    gql = """
    query($episodeId:String!){
      episode(_id:$episodeId){
        sourceUrls
      }
    }
    """

    r = requests.post(API,json={"query":gql,"variables":{"episodeId":episode_id}},headers=HEADERS).json()
    return r["data"]["episode"]["sourceUrls"][0]["sourceUrl"]

# ---------------- AES DECRYPT ----------------

def decrypt_blob(blob):
    key = hashlib.sha256(b"SimtVuagFbGR2K7P").digest()
    raw = base64.b64decode(blob)

    iv = raw[:12]
    ciphertext = raw[12:-16]

    ctr = Counter.new(128, initial_value=int.from_bytes(iv+b"\x00\x00\x00\x02","big"))
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)

    return cipher.decrypt(ciphertext).decode()

# ---------------- HEX DECODE ----------------

def decode_provider_url(hex_string):
    try:
        return bytes.fromhex(hex_string).decode("utf-8")
    except:
        return None

def extract_providers(text):
    data = json.loads(text)
    return [(s["sourceName"], decode_provider_url(s["sourceUrl"])) for s in data]

# ---------------- GET M3U8 ----------------

def extract_m3u8(embed):
    if embed.startswith("//"):
        url = "https:" + embed
    elif embed.startswith("http"):
        url = embed
    else:
        url = "https://" + embed

    html = requests.get(url,headers=HEADERS).text
    return re.search(r'https://.*master\.m3u8', html).group(0)

# ---------------- QUALITY PICKER ----------------

def choose_quality(master_url):
    playlist = requests.get(master_url,headers=HEADERS).text
    streams = re.findall(r'RESOLUTION=\d+x(\d+).*?\n(.*)', playlist)
    streams = sorted(streams,key=lambda x:int(x[0]),reverse=True)

    for i,(res,url) in enumerate(streams):
        print(f"{i+1}. {res}p")

    idx=int(input("Choose quality: ")) - 1
    return master_url.rsplit("/",1)[0] + "/" + streams[idx][1]

# ---------------- PLAYER ----------------

def play_video(url,title):
    subprocess.run(["mpv",f"--force-media-title={title}",url])

# ---------------- MAIN ----------------

def main():
    query=input("Search anime: ")
    show_id,name=search_anime(query)

    eps=get_episode_list(show_id)
    print("Total Episodes:",len(eps))

    ep=input("Episode number: ")
    print("Extracting sources...")

    episode_id=get_episode_id(show_id,ep)
    blob=get_episode_blob(episode_id)
    decrypted=decrypt_blob(blob)
    providers=extract_providers(decrypted)

    master=extract_m3u8(providers[0][1])
    final_stream=choose_quality(master)

    play_video(final_stream,f"{name} Episode {ep}")

if __name__=="__main__":
    main()
