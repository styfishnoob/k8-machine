from tqdm.notebook import tqdm
import pandas as pd
import re

def get_race_returns(html_path_list: list):
  """
  取得したraceページから、払い戻しデータを抽出しDataFrameに変換\n
  dfsの1番目に単勝～馬連、2番目にワイド～3連単がある\n
  0: 買い方 1: 倍率 2: 人気
  """

  return_tables= {}

  for html_path in tqdm(html_path_list):
    with open(html_path, "rb") as f:
      html = f.read()

      html = html.replace(b"<br />", b"br")
      dfs = pd.read_html(html)
      df = pd.concat([dfs[1], dfs[2]])

      race_id = re.findall("(?<=race/)\d+", html_path)[0]
      df.index = [race_id] * len(df)
      return_tables[race_id] = df

  return_tables_df = pd.concat([return_tables[key] for key in return_tables])

  return return_tables_df