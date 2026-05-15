FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "run.py"]
