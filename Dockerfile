FROM python:3.12-slim

# Calibre's installer needs these for its self-extracting binaries and font/rendering libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    libxcb-cursor0 \
    libegl1 \
    libopengl0 \
    libxkbcommon0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxi6 \
    libfontconfig1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY watcher.py .

ENV WATCH_DIR=/data/books
VOLUME ["/data/books"]

CMD ["python", "watcher.py"]
