from tqdm.notebook import tqdm
import pandas as pd
import re

def get_horse_peds(html_path_list: list):
  """
  取得したhorse/pedページから、血統データを抽出しDataFrameに変換
  """

  peds = {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()
      df = pd.read_html(html)[0]
      generations = {}
      horse_id = re.findall("(?<=ped/)\d+", html_path)[0]
      for i in reversed(range(5)):
        generations[i] = df[i]
        df.drop([i], axis=1, inplace=True)
        df = df.drop_duplicates()

      ped = pd.concat([generations[i] for i in range(5)]).rename(horse_id)
      peds[horse_id] = ped.reset_index(drop=True)
  
  peds_df = pd.concat([peds[key] for key in peds], axis=1).T.add_prefix('peds_')
  return peds_df