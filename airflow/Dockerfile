FROM apache/airflow:2.8.4-python3.10

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libgomp1 \
    libquadmath0 \
    git \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
