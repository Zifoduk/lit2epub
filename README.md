# lit2epub

Watches a folder and automatically converts any `.lit` file dropped into it
to `.epub`, using Calibre's `ebook-convert`. Runs as a long-lived Docker
container.

## Usage

```bash
docker compose up -d --build
```

Drop `.lit` files into `./books/`. Each one is converted in place to a
`.epub` file alongside it (e.g. `books/mybook.lit` -> `books/mybook.epub`).

Existing `.lit` files in the folder are converted on startup. Files already
converted (an `.epub` newer than its `.lit`) are skipped.

## Configuration

Environment variables (set in `docker-compose.yml`):

- `WATCH_DIR` — directory to watch (default `/data/books`)
- `SCAN_INTERVAL` — seconds between fallback full-directory scans, in case a
  filesystem event is missed (default `30`)
- `STABLE_SECONDS` — seconds a file's size must stay unchanged before it's
  considered fully written and safe to convert (default `2`)

## Notes

- Input files must be DRM-free; Calibre cannot convert DRM-protected `.lit`
  files.
- Logs are written to stdout: `docker compose logs -f`.
