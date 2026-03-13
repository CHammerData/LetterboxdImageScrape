# LetterboxdImageScrape

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Last Commit](https://img.shields.io/github/last-commit/HammerPatriot/LetterboxdImageScrape)
![Repo Size](https://img.shields.io/github/repo-size/HammerPatriot/LetterboxdImageScrape)
![Libraries: curl-cffi](https://img.shields.io/badge/curl--cffi-0.7%2B-orange)
![Libraries: BeautifulSoup](https://img.shields.io/badge/beautifulsoup4-4.12%2B-orange)
![Libraries: Pillow](https://img.shields.io/badge/Pillow-10%2B-orange)

Scrapes a [Letterboxd](https://letterboxd.com) user's diary for a given year, downloads every film's poster, and assembles them into shareable composite collage images — perfect for posting to social media.

---

## Features

- Scrapes any public Letterboxd diary by username and year
- Optionally removes duplicate entries (re-watches)
- Orders films chronologically or by most-recent
- Splits posters across N collage images, each arranged in a square grid
- 4× upscaled output for high-resolution sharing
- Full CLI with `argparse` — no code editing needed
- Output saved to `./output/<username>_<year>/` — staging files cleaned up automatically

---

## Requirements

- Python 3.10+

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python LetterboxdScraper.py <username> [options]
```

| Argument | Default | Description |
|---|---|---|
| `username` | *(required)* | Letterboxd username |
| `--year YEAR` | `2024` | Diary year to scrape |
| `--images N` | `4` | Number of output collage images |
| `--no-duplicates` | off | Remove re-watched films |
| `--sort SORT` | `chronological` | Film ordering (see table below) |
| `--verbose` / `-v` | off | Enable debug logging |

**Sort options:**

| Value | Order |
|---|---|
| `chronological` | Oldest watch date first |
| `recent` | Newest watch date first |
| `personal_rating` | Your rating, highest first |
| `personal_rating_asc` | Your rating, lowest first |
| `letterboxd_rating` | Community average rating, highest first |
| `letterboxd_rating_asc` | Community average rating, lowest first |
| `name` | Film title, A → Z |
| `release_year` | Release year, oldest first |
| `runtime` | Runtime, shortest first |
| `runtime_desc` | Runtime, longest first |
| `popularity` | Letterboxd popularity, most popular first |
| `shuffle` | Random |

**Examples:**

```bash
# Scrape 2023 diary, produce 4 collages in chronological order
python LetterboxdScraper.py someuser --year 2023

# 6 collages, no re-watches, most-recent-first
python LetterboxdScraper.py someuser --year 2024 --images 6 --no-duplicates --sort recent
```

Output images are saved to `./output/<username>_<year>/` (`0.jpg`, `1.jpg`, …).

---

## How It Works

1. **Diary scrape** — Uses `curl_cffi` (browser TLS impersonation) to fetch each paginated diary page and collect film URLs from `data-item-link` attributes on rendered React components.
2. **Poster resolution** — Visits each film page and extracts the portrait poster URL from the JSON-LD `<script>` block (`"image"` field on the CDN).
3. **Download** — Saves numbered JPEGs to a hidden `.staging` subfolder.
4. **Collage assembly** — Distributes posters evenly across N output images, arranges each batch in a square grid on a black canvas, upscales 4× for shareable resolution, then deletes the staging folder.

---

## License

MIT
