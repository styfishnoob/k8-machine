import random
import re
import time
import traceback
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.notebook import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from const import user_agents, url_paths

def scrape_kaisai_date(from_, to_):
  kaisai_date_list = []
  for date in tqdm(pd.date_range(from_, to_, freq="MS")):
    url = f"https://race.netkeiba.com/top/calendar.html?year={date.year}&month={date.month}"
    headers = { 'User-Agent': random.choice(user_agents.USER_AGENTS) }
    request = Request(url, headers=headers)
    
    response = urlopen(request).read()
    time.sleep(1)
    html = response.decode("EUC-JP") 
    soup = BeautifulSoup(html, features="lxml")

    a_list = soup.find("table", class_="Calendar_Table").find_all("a")

    for a in a_list:
      kaisai_date = re.findall(r"kaisai_date=(\d{8})", a["href"])[0]
      kaisai_date_list.append(kaisai_date)

  return kaisai_date_list

def scrape_race_id_list(kaisai_date_list: list[str]):
  """
  kaisai_date_list: 開催日(yyyymmdd)のリスト
  """

  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-gpu")
  options.add_argument("--headless")

  race_id_list = []

  with webdriver.Remote(command_executor=url_paths.SELENIARM_HOST, options=options) as driver:
    for kaisai_date in tqdm(kaisai_date_list):
      url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
      try:
        driver.get(url)
        time.sleep(1)
        li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
        for li in li_list:
          href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
          race_id = re.findall(r"race_id=(\d{12})", href)
          race_id_list.append(race_id)

      except:
        print(f"stopped at {url}")
        print(traceback.format_exc())
        break

    return race_id_list
      
