FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    wget curl gnupg lsb-release gzip && \
    pip install --no-cache-dir \
        google-cloud-storage \
        google-cloud-bigquery && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY backup.py /backup.py
COPY restore.py /restore.py

ENTRYPOINT ["python", "/backup.py"]