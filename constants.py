import json
import yaml

diff = ["PST", "PRS", "FTR", "BYD"]
diff_fn = ["Past", "Present", "Future", "Beyond"]
clr = ["F", "NC", "FR", "PM", "EC", "HC"]
partners_names = ["Hikari", "Tairitsu", "Kou", "Sapphire", "Lethe", "unknown_icon", "[Axium] Tairitsu",
                  "[Grievous] Tairitsu", "unknown_icon", "Hikari & Fisica", "Ilith", "Eto", "Luna", "Shirabe",
                  "[Zero] Hikari", "[Fracture] Hikari", "[Summer] Hikari", "[Summer] Tairitsu", "Tairitsu & Trin",
                  "Ayu", "[Winter] Eto & Luna", "Yume", "Hikari & Seine", "Saya", "[Grievous] Tairistu & Chuni Penguin",
                  "Chuni Pinguin", "Haruna", "Nono", "[MTA-XXX] Pandora Nemesis", "[MDA-21] Regulus", "Kanae",
                  "[Fantasia] Hikari", "[Sonata] Tairitsu", "Sia", "DORO*C", "[Tempest] Tairitsu",
                  "[E/S Primera] Brillante", "[Summer] Ilith", "[Etude] Saya", "Alice & Tenniel", "Luna & Mia",
                  "Areus", "Seele", "Isabelle", "Mir", "Lagrange"]

# Asset links
partners = "http://119.23.30.103:8080/ArcAssets/icon/"
cover = "http://119.23.30.103:8080/ArcAssets/cover/"


def get_api():
    with open("config.yaml", "r", encoding="UTF-8") as f:
        return yaml.load("".join(f.readlines()), Loader=yaml.FullLoader)["api"]["url"]


def get_ua():
    with open("config.yaml", "r", encoding="UTF-8") as f:
        return yaml.load("".join(f.readlines()), Loader=yaml.FullLoader)["api"]["user-agent"]


def get_songlist():
    with open("ArcSongList.json", "r", encoding="UTF-8") as f:
        return json.load(f)


api_url = get_api()
api_ua = get_ua()
headers = {"User-Agent": api_ua}

songlist = get_songlist()
