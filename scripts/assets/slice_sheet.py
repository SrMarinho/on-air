"""Slice a sheet of separate UI elements into individual trimmed PNGs.

Elements are found as connected opaque regions (merging nearby parts), ordered row by row,
and written with the names given. The soft glow halo around generated art is removed.

Usage (from code): slice_sheet(sheet_path, out_paths, merge_radius)
CLI preview:       python slice_sheet.py <sheet.png>   -> prints element boxes in order
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SOLID_ALPHA = 200  # below this is glow/shadow
MERGE_RADIUS = 3
KEEP_EDGE = 2  # px of anti-aliased edge kept around solid pixels
MIN_PIXELS = 400


def find_elements(rgba: np.ndarray, merge_radius: int = MERGE_RADIUS) -> list[tuple[int, int, int, int, np.ndarray]]:
    solid = rgba[:, :, 3] >= SOLID_ALPHA
    merged = ndi.binary_dilation(solid, iterations=merge_radius)
    labels, count = ndi.label(merged)
    elements = []
    for index, box in enumerate(ndi.find_objects(labels), start=1):
        mask = (labels[box] == index) & solid[box]
        if mask.sum() < MIN_PIXELS:
            continue
        elements.append((box[0].start, box[0].stop, box[1].start, box[1].stop, mask))
    # row-major: group by vertical center into rows, then left→right
    elements.sort(key=lambda e: (e[0] + e[1]) / 2)
    rows: list[list] = []
    for e in elements:
        center = (e[0] + e[1]) / 2
        if rows and abs(center - np.mean([(r[0] + r[1]) / 2 for r in rows[-1]])) < 80:
            rows[-1].append(e)
        else:
            rows.append([e])
    return [e for row in rows for e in sorted(row, key=lambda e: e[2])]


def extract(rgba: np.ndarray, element: tuple[int, int, int, int, np.ndarray]) -> Image.Image:
    y0, y1, x0, x1, mask = element
    # Keep translucent interiors (ghosts, fills) but drop the glow outside the outline.
    keep = ndi.binary_fill_holes(ndi.binary_dilation(mask, iterations=KEEP_EDGE))
    crop = rgba[y0:y1, x0:x1].copy()
    crop[~keep] = 0
    image = Image.fromarray(crop)
    bbox = image.getbbox()
    return image.crop(bbox) if bbox else image


def slice_sheet(sheet: Path, outputs: list[Path], merge_radius: int = MERGE_RADIUS) -> None:
    rgba = np.array(Image.open(sheet).convert("RGBA"))
    elements = find_elements(rgba, merge_radius)
    if len(elements) != len(outputs):
        raise SystemExit(f"{sheet.name}: found {len(elements)} elements, expected {len(outputs)}")
    for element, out in zip(elements, outputs, strict=True):
        out.parent.mkdir(parents=True, exist_ok=True)
        extract(rgba, element).save(out, optimize=True)


if __name__ == "__main__":
    data = np.array(Image.open(sys.argv[1]).convert("RGBA"))
    for i, (y0, y1, x0, x1, _) in enumerate(find_elements(data)):
        print(f"{i:2} x={x0:4}-{x1:4} y={y0:4}-{y1:4}")
