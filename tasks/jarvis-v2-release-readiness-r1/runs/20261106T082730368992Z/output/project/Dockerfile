FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Server image only needs core deps — audio/GUI/vision stay on desktop installs
COPY requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt

COPY app ./app
COPY assets ./assets
COPY frontend ./frontend
COPY config.yaml.example ./config.yaml

EXPOSE 8000

CMD ["python", "-m", "app.main"]
