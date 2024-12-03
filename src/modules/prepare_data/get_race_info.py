from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_race_info(html_path_list: list):
  """
  取得したraceページから、レース場のコンディションなどを抽出しDataFrameに変換
  """

  race_infos= {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()
      soup = BeautifulSoup(html, "html.parser")

      texts = (
        soup.find("div", attrs={"class": "data_intro"}).find_all("p")[0].text
        + soup.find("div", attrs={"class": "data_intro"}).find_all("p")[1].text
      )

      info = re.findall(r"\w+", texts)
      df = pd.DataFrame()

      for text in info:
        if text in ["芝", "ダート"]:
          df["race_type"] = [text]
        
        if "障" in text:
          df["race_type"] = ["障害"]

        if "m" in text:
          df["course_len"] = [int(re.findall(r"\d+", text)[-1])]

        if text in ["良", "稍重", "重", "不良"]:
          df["ground_state"] = [text]

        if text in ["曇","晴","雨","小雨","小雪","雪"]:
          df["weather"] = [text]
        
        if "年" in text:
          df["date"] = [text]

      race_id = re.findall("(?<=race/)\d+", html_path)[0]
      df.index = [race_id] * len(df)

      race_infos[race_id] = df

  race_infos_df = pd.concat([race_infos[key] for key in race_infos])

  return race_infos_df