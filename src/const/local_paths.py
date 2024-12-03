import os

ROOT_DIR: str = os.path.abspath("/workspace")
DATA_DIR: str = os.path.join(ROOT_DIR, "data")

HTML_DIR: str = os.path.join(DATA_DIR, "html")
HTML_RACE_DIR: str = os.path.join(HTML_DIR, "race")
HTML_HORSE_DIR: str = os.path.join(HTML_DIR, "horse")
HTML_PED_DIR: str = os.path.join(HTML_DIR, "ped")