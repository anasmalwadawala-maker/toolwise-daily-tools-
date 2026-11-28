FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOWNLOAD_DIR=/tmp/linkora-downloads \
    PORT=8080 \
    PATH="/usr/local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN python -m compileall -q app

RUN useradd --create-home --uid 10001 linkora \
    && mkdir -p /tmp/linkora-downloads \
    && chown -R linkora:linkora /app /tmp/linkora-downloads
USER linkora

EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
