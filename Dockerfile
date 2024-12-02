# ベースイメージとしてPythonを使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /workspace

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && apt-get clean

# Pythonライブラリをインストール
RUN pip install --upgrade pip && pip install \
    pandas \
    numpy \
    tqdm \
    scikit-learn \
    lightgbm \
    requests \
    beautifulsoup4 \
    matplotlib \
    optuna \
    jupyter \
    lxml

# コンテナが起動するたびに /workspace に移動
CMD ["bash"]
