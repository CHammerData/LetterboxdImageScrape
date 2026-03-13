"""
letterboxd_scraper/scraper/posters.py
======================================
Resolves and downloads film poster images as in-memory PIL Images.

No files are written here — callers receive ``PIL.Image.Image`` objects
and decide what to do with them (display in a UI, save to disk, etc.).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from io import BytesIO

from bs4 import BeautifulSoup
from curl_cffi import requests
from PIL import Image

from letterboxd_scraper.config import IMPERSONATE, LETTERBOXD_BASE, ScraperConfig

log = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], None]


def get_poster_urls(
    film_links: list[str],
    config: ScraperConfig,
    progress: ProgressCallback | None = None,
) -> list[str]:
    """Visit each film page and extract its portrait poster CDN URL.

    The URL is read from the JSON-LD ``<script>`` block on the film page.
    Letterboxd's ``og:image`` returns a landscape backdrop; the JSON-LD
    ``"image"`` field points to the actual 2:3 portrait poster.

    Args:
        film_links: Relative film paths from
                    :func:`~letterboxd_scraper.scraper.diary.get_film_links`.
        config:     Populated :class:`~letterboxd_scraper.config.ScraperConfig`.
        progress:   Optional ``(current, total)`` callback.

    Returns:
        List of absolute CDN poster URLs, in the same order as *film_links*.
        Films without a discoverable poster are skipped (a warning is logged).
    """
    poster_urls: list[str] = []
    total = len(film_links)

    for i, film_path in enumerate(film_links, 1):
        url = f"{LETTERBOXD_BASE}{film_path}"
        response = requests.get(url, impersonate=IMPERSONATE, timeout=config.request_timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        ld_script = soup.find("script", type="application/ld+json")
        poster_url: str | None = None

        if ld_script and ld_script.string:
            match = re.search(r'"image"\s*:\s*"([^"]+)"', ld_script.string)
            if match:
                poster_url = match.group(1)

        if poster_url:
            poster_urls.append(poster_url)
            log.debug("Resolved poster URL %d / %d", i, total)
        else:
            log.warning("No JSON-LD poster found for %s — skipping", url)

        if progress:
            progress(i, total)

    return poster_urls


def download_poster_images(
    poster_urls: list[str],
    config: ScraperConfig,
    progress: ProgressCallback | None = None,
) -> list[Image.Image]:
    """Download poster images and return them as in-memory PIL Images.

    No files are written to disk.  The returned list is ready to be passed
    directly to :func:`~letterboxd_scraper.composer.build_all_collages`.

    Args:
        poster_urls: CDN URLs from :func:`get_poster_urls`.
        config:      Populated :class:`~letterboxd_scraper.config.ScraperConfig`.
        progress:    Optional ``(current, total)`` callback.

    Returns:
        List of ``PIL.Image.Image`` objects in RGB mode, same order as
        *poster_urls*.
    """
    images: list[Image.Image] = []
    total = len(poster_urls)

    for i, url in enumerate(poster_urls, 1):
        response = requests.get(url, impersonate=IMPERSONATE, timeout=config.request_timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
        log.debug("Downloaded poster %d / %d", i, total)
        if progress:
            progress(i, total)

    return images
