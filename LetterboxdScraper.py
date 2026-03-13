"""
LetterboxdScraper.py
====================
CLI entry point.  All scraping and composition logic lives in the
``letterboxd_scraper`` package — this file is a thin argument-parsing wrapper.

Usage:
    python LetterboxdScraper.py <username> [--year YEAR] [--images N]
                                [--no-duplicates] [--sort {chronological,recent}]
                                [--output DIR] [-v]
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from letterboxd_scraper import (
    PHASE_COMPOSE,
    PHASE_DIARY,
    PHASE_DOWNLOAD,
    PHASE_POSTERS,
    ScraperConfig,
    run,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Human-readable labels for each pipeline phase
_PHASE_LABELS = {
    PHASE_DIARY: "Scraping diary",
    PHASE_POSTERS: "Fetching poster URLs",
    PHASE_DOWNLOAD: "Downloading posters",
    PHASE_COMPOSE: "Building collages",
}


def save_collages(collages: list, output_dir: Path) -> list[Path]:
    """Save a list of PIL Images to *output_dir* as ``0.jpg``, ``1.jpg``, …

    Args:
        collages:   Finished collage PIL Images from :func:`~letterboxd_scraper.run`.
        output_dir: Directory to write into (created if it does not exist).

    Returns:
        List of paths to the saved files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for i, img in enumerate(collages):
        path = output_dir / f"{i}.jpg"
        img.save(path)
        log.info("Saved collage %d → %s", i, path)
        saved.append(path)
    return saved


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="LetterboxdScraper",
        description="Build shareable poster collages from a Letterboxd diary.",
    )
    parser.add_argument("username", help="Letterboxd username")
    parser.add_argument(
        "--year",
        default="2024",
        help="Diary year to scrape (default: %(default)s)",
    )
    parser.add_argument(
        "--images",
        type=int,
        default=4,
        dest="image_count",
        help="Number of output collage images (default: %(default)s)",
    )
    parser.add_argument(
        "--no-duplicates",
        action="store_true",
        dest="remove_duplicates",
        help="Remove duplicate film entries (re-watches)",
    )
    parser.add_argument(
        "--sort",
        choices=[
            "chronological",         # oldest watch date first
            "recent",                # newest watch date first
            "diary_rating",       # diary entry rating, highest first
            "diary_rating_asc",   # diary entry rating, lowest first
            "letterboxd_rating",     # community rating, highest first
            "letterboxd_rating_asc", # community rating, lowest first
            "name",                  # film title A → Z
            "release_year",          # oldest release year first
            "runtime",               # shortest runtime first
            "runtime_desc",          # longest runtime first
            "popularity",            # most popular on Letterboxd first
            "shuffle",               # random order
        ],
        default="chronological",
        metavar="SORT",
        help=(
            "Film ordering in collages (default: %(default)s). "
            "Choices: chronological, recent, diary_rating, diary_rating_asc, "
            "letterboxd_rating, letterboxd_rating_asc, name, release_year, "
            "runtime, runtime_desc, popularity, shuffle."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: ./output/<username>_<year>/)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = ScraperConfig(
        username=args.username,
        year=args.year,
        image_count=args.image_count,
        remove_duplicates=args.remove_duplicates,
        sort=args.sort,
    )

    def on_progress(phase: str, current: int, total: int) -> None:
        label = _PHASE_LABELS.get(phase, phase)
        log.info("%s: %d / %d", label, current, total)

    result = run(config, progress=on_progress)

    output_dir = args.output or Path("output") / f"{config.username}_{config.year}"
    save_collages(result.collages, output_dir)

    log.info(
        "Done — %d films, %d posters, distribution: %s",
        result.film_count,
        result.poster_count,
        result.poster_distribution,
    )
    log.info("Output saved to: %s", output_dir)
