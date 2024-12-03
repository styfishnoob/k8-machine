from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_race_results(html_path_list: list):
  """
  取得したraceページから、レース結果を抽出しDataFrameに変換
  """

  race_results= {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()
      df = pd.read_html(html)[0]
      soup = BeautifulSoup(html, "html.parser")

      horse_id_list = []
      horse_a_list = soup.find("table", attrs={"summary": "レース結果"}).find_all(
        "a", attrs={"href": re.compile("^/horse")}
      )

      for a in horse_a_list:
        horse_id = re.findall(r"\d+", a["href"])
        horse_id_list.append(horse_id[0])

      jockey_id_list = []
      jockey_a_list = soup.find("table", attrs={"summary": "レース結果"}).find_all(
        "a", attrs={"href": re.compile("^/jockey")}
      )

      for a in jockey_a_list:
        jockey_id = re.findall(r"\d+", a["href"])
        jockey_id_list.append(jockey_id[0])
      
      df["horse_id"] = horse_id_list
      df["jockey_id"] = jockey_id_list

      race_id = re.findall("(?<=race/)\d+", html_path)[0]
      df.index = [race_id] * len(df)

      race_results[race_id] = df
  
  race_results_df = pd.concat([race_results[key] for key in race_results])

  return race_results_df