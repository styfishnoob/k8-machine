from tqdm.notebook import tqdm
import pandas as pd
import re

def get_horse_results(html_path_list: list):
  """
  取得したhorseページから、馬の過去成績データを抽出しDataFrameに変換
  """

  horse_results = {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()
      df = pd.read_html(html)[2]
      horse_id = re.findall("(?<=horse/)\d+", html_path)[0]

      df.index = [horse_id] * len(df)
      horse_results[horse_id] = df
  
  horse_results_df = pd.concat([horse_results[key] for key in horse_results])
  return horse_results_df