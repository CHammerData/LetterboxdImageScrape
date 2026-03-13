"""
letterboxd_scraper
==================
Library for scraping Letterboxd diary posters and assembling them into
shareable collage images.

Minimal usage::

    from letterboxd_scraper import ScraperConfig, run

    result = run(ScraperConfig(username="someuser", year="2024"))
    for img in result.collages:
        img.save(f"collage_{i}.jpg")

With progress (e.g. Streamlit)::

    import streamlit as st
    from letterboxd_scraper import ScraperConfig, run, PHASE_POSTERS

    bar = st.progress(0, text="Starting…")

    def on_progress(phase: str, current: int, total: int) -> None:
        bar.progress(current / total, text=f"{phase}  {current}/{total}")

    result = run(ScraperConfig("someuser", "2024"), progress=on_progress)
    for img in result.collages:
        st.image(img)
"""

from letterboxd_scraper.config import ScraperConfig, SortOrder
from letterboxd_scraper.pipeline import (
    PHASE_COMPOSE,
    PHASE_DIARY,
    PHASE_DOWNLOAD,
    PHASE_POSTERS,
    PipelineProgressCallback,
    ScrapeResult,
    run,
)

__all__ = [
    "ScraperConfig",
    "SortOrder",
    "run",
    "ScrapeResult",
    "PipelineProgressCallback",
    "PHASE_DIARY",
    "PHASE_POSTERS",
    "PHASE_DOWNLOAD",
    "PHASE_COMPOSE",
]
