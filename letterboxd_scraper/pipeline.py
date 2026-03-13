"""
letterboxd_scraper/pipeline.py
================================
Orchestrates the full scrape-download-compose pipeline.

This module never touches the filesystem.  It returns a :class:`ScrapeResult`
containing finished PIL Image objects so the caller (CLI, Streamlit, FastAPI,
test, etc.) decides what to do with them.

Example — Streamlit usage::

    from letterboxd_scraper import ScraperConfig, run, PHASE_POSTERS
    import streamlit as st

    bar = st.progress(0, text="Starting…")

    def on_progress(phase: str, current: int, total: int) -> None:
        bar.progress(current / total, text=f"{phase}  {current}/{total}")

    result = run(ScraperConfig("someuser", "2024"), progress=on_progress)

    for img in result.collages:
        st.image(img)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image

from letterboxd_scraper.composer import build_all_collages
from letterboxd_scraper.config import ScraperConfig
from letterboxd_scraper.scraper.diary import get_film_links, get_page_count
from letterboxd_scraper.scraper.posters import download_poster_images, get_poster_urls

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase label constants — passed to the progress callback so the UI can
# display a human-readable stage name alongside the numeric progress.
# ---------------------------------------------------------------------------
PHASE_DIARY = "diary"
PHASE_POSTERS = "posters"
PHASE_DOWNLOAD = "download"
PHASE_COMPOSE = "compose"

# Callback type: (phase, current, total)
PipelineProgressCallback = Callable[[str, int, int], None]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ScrapeResult:
    """Returned by :func:`run` after a successful pipeline execution.

    Attributes:
        collages:             Finished collage PIL Images.
        film_count:           Number of diary entries found (before dedup).
        poster_count:         Number of posters successfully resolved & downloaded.
        poster_distribution:  How many posters were assigned to each collage.
    """

    collages: list[Image.Image]
    film_count: int
    poster_count: int
    poster_distribution: list[int]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(
    config: ScraperConfig,
    progress: PipelineProgressCallback | None = None,
) -> ScrapeResult:
    """Execute the full scrape → resolve → download → compose pipeline.

    Args:
        config:   Fully populated :class:`~letterboxd_scraper.config.ScraperConfig`.
        progress: Optional three-argument callback invoked throughout the run::

                      progress(phase: str, current: int, total: int)

                  *phase* is one of the ``PHASE_*`` constants in this module.
                  *current* and *total* are the step index within that phase.

    Returns:
        :class:`ScrapeResult` with finished collage Images and diagnostic counts.
    """
    # -- Phase 1: count diary pages, then scrape film links ------------------
    log.info("Scraping diary for %s (%s)", config.username, config.year)
    pages, entries = get_page_count(config)
    log.info("%d entries across %d page(s)", entries, pages)

    film_links = get_film_links(
        config,
        pages,
        progress=lambda c, t: progress(PHASE_DIARY, c, t) if progress else None,
    )
    film_count = len(film_links)
    log.info("Film links collected: %d", film_count)

    # -- Phase 2: resolve portrait poster CDN URLs ---------------------------
    log.info("Resolving poster URLs…")
    poster_urls = get_poster_urls(
        film_links,
        config,
        progress=lambda c, t: progress(PHASE_POSTERS, c, t) if progress else None,
    )
    log.info("Poster URLs resolved: %d", len(poster_urls))

    # -- Phase 3: download posters into memory -------------------------------
    log.info("Downloading posters…")
    posters = download_poster_images(
        poster_urls,
        config,
        progress=lambda c, t: progress(PHASE_DOWNLOAD, c, t) if progress else None,
    )
    log.info("Posters downloaded: %d", len(posters))

    # -- Phase 4: assemble collages ------------------------------------------
    log.info("Building collages…")

    # Track distribution for the result before building
    from letterboxd_scraper.composer import distribute_posters
    distribution = distribute_posters(len(posters), config.image_count)

    collages = build_all_collages(
        posters,
        config,
        progress=lambda c, t: progress(PHASE_COMPOSE, c, t) if progress else None,
    )
    log.info("Collages built: %d", len(collages))

    return ScrapeResult(
        collages=collages,
        film_count=film_count,
        poster_count=len(posters),
        poster_distribution=distribution,
    )
