import os

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
DEVELOPER_KEY = ""

try:
    from app.crawler.config_local import *
except ImportError:
    pass