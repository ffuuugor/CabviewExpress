import os

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
CITIES_PATH = os.path.join(DATA_DIR, "cities15000.txt")
DEVELOPER_KEY = ""

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

QUERY_LIST = ["train view", "cabview", "cab view", "cabride", "cab ride", "rail view"]

try:
    from app.crawler.config_local import *
except ImportError:
    pass