"""
letterboxd_scraper/config.py
============================
Configuration dataclass and shared constants for the scraper library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LETTERBOXD_BASE: str = "https://letterboxd.com"
ENTRIES_PER_PAGE: int = 50
IMPERSONATE: str = "chrome"  # curl_cffi browser profile — bypasses Cloudflare

# ---------------------------------------------------------------------------
# Sort options
#
# Each value maps to a Letterboxd diary URL slug (/by/<slug>/).
# Sorting is handled server-side by Letterboxd — no local sorting needed.
# ---------------------------------------------------------------------------
SortOrder = Literal[
    "recent",               # newest watch date first (Letterboxd default)
    "chronological",        # oldest watch date first
    "diary_rating",         # diary entry rating, highest first
    "diary_rating_asc",     # diary entry rating, lowest first
    "letterboxd_rating",    # community average rating, highest first
    "letterboxd_rating_asc",# community average rating, lowest first
    "name",                 # film title, A → Z
    "release_year",         # film release year, oldest first
    "runtime",              # film runtime, shortest first
    "runtime_desc",         # film runtime, longest first
    "popularity",           # Letterboxd popularity, most popular first
    "shuffle",              # random order
]

# Maps each SortOrder value to the Letterboxd /by/<slug>/ URL segment.
# A value of None means use the default diary URL (no /by/ appended).
SORT_URL_SLUGS: dict[str, str | None] = {
    "recent":                None,
    "chronological":         "date-earliest",
    "diary_rating":       "entry-rating",
    "diary_rating_asc":   "entry-rating-lowest",
    "letterboxd_rating":     "rating",
    "letterboxd_rating_asc": "rating-lowest",
    "name":                  "name",
    "release_year":          "release-earliest",
    "runtime":               "shortest",
    "runtime_desc":          "longest",
    "popularity":            "popular",
    "shuffle":               "shuffle",
}


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass
class ScraperConfig:
    """All tuneable parameters for a single scrape run.

    Attributes:
        username:          Letterboxd username to scrape.
        year:              Four-digit diary year (e.g. ``"2024"``).
        image_count:       Number of output collage images to produce.
        remove_duplicates: If ``True``, re-watched films appear only once.
        sort:              One of the :data:`SortOrder` values — controls
                           the order films appear in the collages.
        request_timeout:   HTTP request timeout in seconds.
        upscale_factor:    Integer multiplier applied to each finished collage.
    """

    username: str
    year: str
    image_count: int = 4
    remove_duplicates: bool = False
    sort: SortOrder = "chronological"
    request_timeout: int = 15
    upscale_factor: int = 4
