import os
import random
import time
from urllib.request import Request, urlopen
from tqdm.notebook import tqdm
from const import local_paths, url_paths, user_agents

def scrape_html(endpoint: str, id_list: list, save_to: str, skip: bool = True):
  html_path_list = []

  for id in tqdm(id_list):
    url = endpoint + id
    headers = { 'User-Agent': random.choice(user_agents.USER_AGENTS) }
    request = Request(url, headers=headers)

    filename = os.path.join(save_to, id + ".bin")
    html_path_list.append(filename)

    if skip and os.path.isfile(filename):
      print("race_id {} skipped".format(id))
      continue

    response = urlopen(request).read()
    html = response.decode("EUC-JP") 

    with open(filename, "wb") as f:
      f.write(html.encode("EUC-JP"))

    time.sleep(1)

  return html_path_list

def scrape_html_race(race_id_list: list, skip: bool = True):
    endpoint = url_paths.RACE_URL
    save_to = local_paths.HTML_RACE_DIR
    return scrape_html(endpoint, race_id_list, save_to, skip)

def scrape_html_horse(horse_id_list: list, skip: bool = True):
    endpoint = url_paths.HORSE_URL
    save_to = local_paths.HTML_HORSE_DIR
    return scrape_html(endpoint, horse_id_list, save_to, skip)

def scrape_html_ped(horse_id_list: list, skip: bool = True):
    endpoint = url_paths.PED_URL
    save_to = local_paths.HTML_PED_DIR
    return scrape_html(endpoint, horse_id_list, save_to, skip)

