FROM apache/airflow:2.7.1-python3.11

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libgomp1 \
    libquadmath0 \
    git \
    openjdk-11-jdk \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
