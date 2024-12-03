FROM python:3.9-slim
WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && apt-get clean

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
