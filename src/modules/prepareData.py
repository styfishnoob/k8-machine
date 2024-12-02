import os
import random
import time
from urllib.request import Request, urlopen
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
]

def getHTMLRace(race_id_list: list, skip: bool = True):
  """
  netkeiba.comのraceディレクトリのhtmlをスクレイピングしてscrape-result/raceに保存する関数
  """

  html_path_list = []

  for race_id in tqdm(race_id_list):
    url = "https://db.netkeiba.com/race/" + race_id
    headers = { 'User-Agent': random.choice(USER_AGENTS) }
    request = Request(url, headers=headers)

    filename = "/workspace/data/html/race/" + race_id + ".bin"
    html_path_list.append(filename)

    if skip and os.path.isfile(filename):
      print("race_id {} skipped".format(race_id))
      continue

    html = urlopen(request).read()

    with open(filename, "wb") as f:
      f.write(html)

    time.sleep(1)
  return html_path_list

def getRawDataResults(html_path_list: list):
  """
  raceページのhtmlを受け取って、レース結果テーブルに変換する
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

      # インデックスをrace_idにする
      race_id = re.findall("(?<=race/)\d+", html_path)[0]
      df.index = [race_id] * len(df)

      race_results[race_id] = df
  
  # pd.DataFrame型にして一つのデータにまとめる
  race_results_df = pd.concat([race_results[key] for key in race_results])

  return race_results_df

def getRawDataInfo(html_path_list: list):
  """
  raceページのhtmlを受け取って、レース情報テーブルに変換する関数
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

  # pd.DataFrame型にして一つのデータにまとめる
  race_infos_df = pd.concat([race_infos[key] for key in race_infos])

  return race_infos_df

def getRawDataReturn(html_path_list: list):
  """
  raceページのhtmlを受け取って、払い戻しテーブルに変換する
  """

  return_tables= {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()

      html = html.replace(b"<br />", b"br")
      dfs = pd.read_html(html)

      # dfsの1番目に単勝～馬連、2番目にワイド～3連単がある
      # 0: 買い方 1: 倍率 2: 人気
      df = pd.concat([dfs[1], dfs[2]])

      race_id = re.findall("(?<=race/)\d+", html_path)[0]
      df.index = [race_id] * len(df)
      return_tables[race_id] = df

  # pd.DataFrame型にして一つのデータにまとめる
  return_tables_df = pd.concat([return_tables[key] for key in return_tables])

  return return_tables_df

def getHTMLHorse(horse_id_list: list, skip: bool = True):
  """
  netkeiba.comのhorseディレクトリのhtmlをスクレイピングしてscrape-result/horseに保存する関数
  """

  html_path_list = []

  for horse_id in tqdm(horse_id_list):
    url = "https://db.netkeiba.com/horse/" + horse_id
    headers = { 'User-Agent': random.choice(USER_AGENTS) }
    request = Request(url, headers=headers)

    filename = "/workspace/data/html/horse/" + horse_id + ".bin"
    html = urlopen(request).read()
    html_path_list.append(filename)

    if skip and os.path.isfile(filename):
      print("horse_id {} skipped".format(horse_id))
      continue

    with open(filename, "wb") as f:
      f.write(html)

    time.sleep(1)
  return html_path_list

def getRawDataHorseResults(html_path_list: list):
  """
  horseページのhtmlを受け取って、馬の過去成績のDataFrameに変換する関数
  """

  horse_results = {}

  with open(html_path_list[0], "rb") as f:
    html = f.read()

    a = pd.read_html(html)[2]
    print(a)

  # for html_path in tqdm(html_path_list):
  #   with open(html_path, "rb") as f:
  #     html = f.read()

  #     df = pd.read_html(html)[3]

  #     if df.columns[0] == "受賞歴":
  #       df = pd.read_html(html)[4]

  #     horse_id = re.findall("(?<=horse/)\d+", html_path)[0]

  #     df.index = [horse_id] * len(df)
  #     horse_results[horse_id] = df
  
  # horse_results_df = pd.concat([horse_results[key] for key in horse_results])
  return
