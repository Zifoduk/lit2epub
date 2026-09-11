#!/usr/bin/env python3
"""Watches a directory for .lit files and converts each to .epub via Calibre's ebook-convert."""
import logging
import os
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

WATCH_DIR = os.environ.get("WATCH_DIR", "/data/books")
STABLE_SECONDS = float(os.environ.get("STABLE_SECONDS", "2"))
POLL_INTERVAL = float(os.environ.get("SCAN_INTERVAL", "30"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("lit2epub")


def epub_path_for(lit_path: str) -> str:
    return os.path.splitext(lit_path)[0] + ".epub"


def is_lit_file(path: str) -> bool:
    return path.lower().endswith(".lit")


def needs_conversion(lit_path: str) -> bool:
    epub_path = epub_path_for(lit_path)
    if not os.path.exists(epub_path):
        return True
    return os.path.getmtime(lit_path) > os.path.getmtime(epub_path)


def wait_until_stable(path: str, seconds: float) -> bool:
    """Wait until a file's size stops changing, so we don't convert a mid-copy file."""
    try:
        last_size = -1
        while True:
            if not os.path.exists(path):
                return False
            size = os.path.getsize(path)
            if size == last_size:
                return True
            last_size = size
            time.sleep(seconds)
    except OSError:
        return False


def convert(lit_path: str) -> None:
    if not wait_until_stable(lit_path, STABLE_SECONDS):
        log.warning("File disappeared before it stabilized: %s", lit_path)
        return

    if not needs_conversion(lit_path):
        return

    epub_path = epub_path_for(lit_path)
    log.info("Converting %s -> %s", lit_path, epub_path)
    result = subprocess.run(
        ["ebook-convert", lit_path, epub_path],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log.info("Converted: %s", epub_path)
    else:
        log.error("Conversion failed for %s:\n%s", lit_path, result.stderr.strip())
        if os.path.exists(epub_path):
            os.remove(epub_path)


def scan_existing(directory: str) -> None:
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if is_lit_file(name):
                full_path = os.path.join(root, name)
                if needs_conversion(full_path):
                    convert(full_path)


class LitHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and is_lit_file(event.src_path):
            convert(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and is_lit_file(event.src_path):
            convert(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and is_lit_file(event.dest_path):
            convert(event.dest_path)


def main() -> int:
    if not os.path.isdir(WATCH_DIR):
        log.error("Watch directory does not exist: %s", WATCH_DIR)
        return 1

    log.info("Watching %s for .lit files", WATCH_DIR)
    scan_existing(WATCH_DIR)

    observer = Observer()
    observer.schedule(LitHandler(), WATCH_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            scan_existing(WATCH_DIR)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

    return 0


if __name__ == "__main__":
    sys.exit(main())
