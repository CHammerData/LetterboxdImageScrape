"""
letterboxd_scraper/composer.py
================================
Assembles lists of poster PIL Images into square-grid collages.

All functions are pure with respect to the filesystem — inputs and outputs
are PIL Image objects.  The CLI or web layer decides whether to save them.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from PIL import Image

from letterboxd_scraper.config import ScraperConfig

ProgressCallback = Callable[[int, int], None]


def distribute_posters(total: int, image_count: int) -> list[int]:
    """Compute how many posters belong to each collage.

    Posters are distributed so that each collage fills a near-square grid.
    The last collage receives any remainder.

    Args:
        total:       Total number of poster images available.
        image_count: Desired number of output collages.

    Returns:
        List of length *image_count* where each element is the poster count
        for that collage.  The values sum to *total*.
    """
    sizes: list[int] = []
    assigned = 0
    for i in range(image_count - 1):
        cols = math.ceil(math.sqrt((total - assigned) / (image_count - i)))
        chunk = cols ** 2
        assigned += chunk
        sizes.append(chunk)
    sizes.append(total - assigned)
    return sizes


def build_collage(posters: list[Image.Image], upscale_factor: int = 4) -> Image.Image:
    """Arrange *posters* into a square grid and return the upscaled result.

    Posters are placed in row-major order on a black canvas.  The canvas is
    sized to the minimum number of rows needed (no empty rows at the bottom).

    Args:
        posters:       Ordered list of PIL Image objects to tile.
        upscale_factor: Integer multiplier applied to the final canvas.

    Returns:
        A single upscaled :class:`PIL.Image.Image` collage.
    """
    cols = math.ceil(math.sqrt(len(posters)))

    # Use the first poster's dimensions as the canonical tile size
    tile_w, tile_h = posters[0].size
    rows = math.ceil(len(posters) / cols)

    canvas = Image.new("RGB", (tile_w * cols, tile_h * rows), (0, 0, 0))

    for idx, poster in enumerate(posters):
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        canvas.paste(poster, (x, y))

    return canvas.resize(
        (canvas.width * upscale_factor, canvas.height * upscale_factor),
        Image.LANCZOS,
    )


def build_all_collages(
    posters: list[Image.Image],
    config: ScraperConfig,
    progress: ProgressCallback | None = None,
) -> list[Image.Image]:
    """Split *posters* across ``config.image_count`` collages.

    Args:
        posters:  All downloaded poster Images in order.
        config:   :class:`~letterboxd_scraper.config.ScraperConfig`
                  (``image_count``, ``upscale_factor`` are read here).
        progress: Optional ``(current, total)`` callback fired after each
                  collage is finished.

    Returns:
        List of finished collage Images.
    """
    distribution = distribute_posters(len(posters), config.image_count)
    collages: list[Image.Image] = []
    offset = 0

    for i, count in enumerate(distribution, 1):
        batch = posters[offset : offset + count]
        collages.append(build_collage(batch, config.upscale_factor))
        offset += count
        if progress:
            progress(i, config.image_count)

    return collages
