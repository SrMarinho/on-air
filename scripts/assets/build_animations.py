"""Build clean, aligned animation atlases for a character.

Source spritesheets (authored, any layout/scale) live in `<character>/sprites/`. For each
animation in `<character>/data/animations.json` this script:

1. Splits frames by connected components (assigned to the authored grid cell by centroid), so
   pixels from neighbouring frames never bleed in.
2. Normalizes character size across sheets (geometric mean of body height and hair-blob area
   vs. `idle`), unless the animation sets `scaleOverride`.
3. Aligns every frame on the same pivot: torso center (x) and feet (y), killing frame jitter.
4. Packs frames in a uniform-cell atlas at `assets/atlases/characters/<character>/<anim>.png`.

Authored fields (never touched): texture, frames, columns, duration, loop, next, scaleOverride.
Generated fields: atlas, atlasColumns, frameWidth, frameHeight, anchor, referenceHeight.

Usage:
  uv run --no-project --with pillow --with numpy --with scipy \
      python scripts/assets/build_animations.py assets/characters/calouro
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ASSETS = Path(__file__).resolve().parents[2] / "assets"
REFERENCE = "idle"
TARGET_HEIGHT = 160  # px of the idle character in the atlas (4x the 40px on-screen height)
ALPHA_THRESHOLD = 16
MIN_COMPONENT_PIXELS = 30
PADDING = 4
MAX_ATLAS_COLUMNS = 8
TORSO_BAND = (0.25, 0.65)  # vertical slice of the body used for the horizontal pivot


@dataclass
class Frame:
    image: np.ndarray  # RGBA, cropped to content
    pivot_x: float  # inside `image`
    height: int


def split_frames(sheet: np.ndarray, frames: int, columns: int) -> list[Frame]:
    alpha = sheet[:, :, 3] > ALPHA_THRESHOLD
    labels, count = ndi.label(ndi.binary_dilation(alpha, iterations=3))
    ids = np.arange(1, count + 1)
    sizes = ndi.sum(alpha, labels, ids)
    centers = ndi.center_of_mass(alpha, labels, ids)
    rows = -(-frames // columns)
    cell_w, cell_h = sheet.shape[1] / columns, sheet.shape[0] / rows

    result = []
    for index in range(frames):
        col, row = index % columns, index // columns
        own = [
            int(i)
            for i, size, (cy, cx) in zip(ids, sizes, centers, strict=True)
            if size >= MIN_COMPONENT_PIXELS and int(cx // cell_w) == col and int(cy // cell_h) == row
        ]
        mask = np.isin(labels, own) & alpha
        ys, xs = np.nonzero(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        image = sheet[y0:y1, x0:x1].copy()
        image[~mask[y0:y1, x0:x1]] = 0
        result.append(Frame(image, torso_center(image), y1 - y0))
    return result


def kebab(name: str) -> str:
    return "".join(f"-{c.lower()}" if c.isupper() else c for c in name)


def torso_center(image: np.ndarray) -> float:
    h = image.shape[0]
    band = image[int(h * TORSO_BAND[0]) : int(h * TORSO_BAND[1]), :, 3] > ALPHA_THRESHOLD
    xs = np.nonzero(band)[1]
    return float(np.median(xs)) if len(xs) else image.shape[1] / 2


def hair_area(sheet: np.ndarray, frames: int) -> float:
    rgb = sheet[:, :, :3].astype(int)
    luminance = (rgb[:, :, 0] * 3 + rgb[:, :, 1] * 6 + rgb[:, :, 2]) / 10
    dark = (sheet[:, :, 3] > ALPHA_THRESHOLD) & (luminance < 55)
    opened = ndi.binary_opening(dark, structure=np.ones((9, 9)))
    labels, count = ndi.label(opened)
    areas = sorted(ndi.sum(opened, labels, range(1, count + 1)), reverse=True)[:frames]
    return float(np.median(areas))


def pack(frames: list[Frame], scale: float) -> tuple[Image.Image, int, int, int, dict[str, float]]:
    scaled = []
    for f in frames:
        img = Image.fromarray(f.image)
        size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        scaled.append((img.resize(size, Image.Resampling.LANCZOS), f.pivot_x * scale))
    half_w = max(max(px, img.width - px) for img, px in scaled)
    cell_w = int(np.ceil(half_w * 2)) + PADDING * 2
    cell_h = max(img.height for img, _ in scaled) + PADDING * 2
    columns = min(len(scaled), MAX_ATLAS_COLUMNS)
    rows = -(-len(scaled) // columns)
    atlas = Image.new("RGBA", (cell_w * columns, cell_h * rows), (0, 0, 0, 0))
    feet_y = cell_h - PADDING
    for i, (img, px) in enumerate(scaled):
        ox = (i % columns) * cell_w + round(cell_w / 2 - px)
        oy = (i // columns) * cell_h + feet_y - img.height
        atlas.alpha_composite(img, (ox, oy))
    anchor = {"x": 0.5, "y": round(feet_y / cell_h, 4)}
    return atlas, columns, cell_w, cell_h, anchor


def main(character_dir: Path) -> None:
    character = character_dir.name
    spec_path = character_dir / "data" / "animations.json"
    animations: dict[str, dict] = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = ASSETS / "atlases" / "characters" / character
    out_dir.mkdir(parents=True, exist_ok=True)

    loaded: dict[str, tuple[list[Frame], float]] = {}
    for name, spec in animations.items():
        path = character_dir / "sprites" / spec["texture"]
        if not path.exists():
            print(f"skip {name}: {path.name} missing")
            continue
        sheet = np.array(Image.open(path).convert("RGBA"))
        frames = split_frames(sheet, spec["frames"], spec["columns"])
        loaded[name] = (frames, hair_area(sheet, spec["frames"]))

    ref_frames, ref_hair = loaded[REFERENCE]
    ref_height = float(np.median([f.height for f in ref_frames]))
    base = TARGET_HEIGHT / ref_height

    for name, (frames, hair) in loaded.items():
        spec = animations[name]
        by_height = ref_height / float(np.median([f.height for f in frames]))
        by_hair = (ref_hair / hair) ** 0.5
        relative = spec.get("scaleOverride") or round((by_height * by_hair) ** 0.5, 4)
        atlas, columns, cell_w, cell_h, anchor = pack(frames, base * relative)
        atlas_path = out_dir / f"{character}-{kebab(name)}.png"
        atlas.save(atlas_path, optimize=True)
        for stale in ("frameWidth", "frameHeight", "anchor", "scale", "referenceHeight"):
            spec.pop(stale, None)
        spec.update(
            atlas=atlas_path.relative_to(ASSETS).as_posix(),
            atlasColumns=columns,
            frameWidth=cell_w,
            frameHeight=cell_h,
            anchor=anchor,
            relativeScale=relative,
        )
        print(f"{name:17} scale={relative:.3f} cell={cell_w}x{cell_h} -> {atlas_path.name}")

    animations[REFERENCE]["referenceHeight"] = TARGET_HEIGHT
    spec_path.write_text(json.dumps(animations, indent=2) + "\n", encoding="utf-8")
    print(f"updated {spec_path.relative_to(ASSETS)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
