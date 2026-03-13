"""
letterboxd_scraper/scraper/diary.py
====================================
Scrapes a Letterboxd diary: counts pages and collects film links.

Sorting is delegated entirely to Letterboxd via the ``/by/<slug>/`` URL
pattern — no local re-ordering is performed here.
"""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Callable

from bs4 import BeautifulSoup
from curl_cffi import requests

from letterboxd_scraper.config import (
    ENTRIES_PER_PAGE,
    IMPERSONATE,
    LETTERBOXD_BASE,
    SORT_URL_SLUGS,
    ScraperConfig,
)

log = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], None]


def _diary_url(config: ScraperConfig, page: int | None = None) -> str:
    """Build the Letterboxd diary URL for the given config and optional page number.

    The sort slug (if any) and pagination suffix are appended automatically.

    Args:
        config: Populated :class:`~letterboxd_scraper.config.ScraperConfig`.
        page:   1-based page number, or ``None`` for the first page.

    Returns:
        Fully qualified diary URL string.
    """
    base = f"{LETTERBOXD_BASE}/{config.username}/films/diary/for/{config.year}"
    slug = SORT_URL_SLUGS.get(config.sort)
    if slug:
        base = f"{base}/by/{slug}"
    if page and page > 1:
        base = f"{base}/page/{page}"
    return base


def get_page_count(config: ScraperConfig) -> tuple[int, int]:
    """Fetch the diary index page and return ``(page_count, entry_count)``.

    Args:
        config: Populated :class:`~letterboxd_scraper.config.ScraperConfig`.

    Returns:
        A ``(pages, entries)`` tuple.

    Raises:
        ValueError: If the entry-count heading cannot be parsed.
    """
    url = _diary_url(config)
    response = requests.get(url, impersonate=IMPERSONATE, timeout=config.request_timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    heading = soup.find("p", class_="ui-block-heading")
    if heading is None:
        raise ValueError(f"Could not find diary heading at {url}")

    match = re.search(r"logged\s+([\d,]+)\s+entr", heading.get_text())
    if not match:
        raise ValueError(f"Unexpected heading format: {heading.get_text()!r}")

    entries = int(match.group(1).replace(",", ""))
    pages = math.ceil(entries / ENTRIES_PER_PAGE)
    return pages, entries


def get_film_links(
    config: ScraperConfig,
    page_count: int,
    progress: ProgressCallback | None = None,
) -> list[str]:
    """Scrape every diary page and return ordered relative film paths.

    Letterboxd renders diary rows as React components; each row's
    ``<div class="react-component">`` carries a ``data-item-link``
    attribute with the relative film path (e.g. ``/film/the-godfather/``).

    Ordering is controlled by ``config.sort``, which is translated to a
    Letterboxd ``/by/<slug>/`` URL so the server returns results pre-sorted.

    Args:
        config:     Populated :class:`~letterboxd_scraper.config.ScraperConfig`.
        page_count: Total pages to scrape, from :func:`get_page_count`.
        progress:   Optional ``(current, total)`` callback.

    Returns:
        Ordered list of relative Letterboxd film paths.
    """
    link_list: list[str] = []

    for page_num in range(1, page_count + 1):
        url = _diary_url(config, page=page_num)
        response = requests.get(url, impersonate=IMPERSONATE, timeout=config.request_timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        for div in soup.find_all("div", class_="react-component"):
            link = div.get("data-item-link", "")
            if link.startswith("/film/"):
                link_list.append(link)

        log.debug("Scraped diary page %d / %d (%s)", page_num, page_count, config.sort)
        if progress:
            progress(page_num, page_count)

    if config.remove_duplicates:
        # dict.fromkeys preserves the server-determined order while deduplicating
        link_list = list(dict.fromkeys(link_list))

    return link_list
