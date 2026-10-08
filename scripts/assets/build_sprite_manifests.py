"""Fill generated geometry in sprite manifests.

- Item manifests (`assets/gameplay/items.json`): adds `bounds` = opaque area of each texture,
  so the client can fit the art to the item's tile footprint regardless of padding.
- Tilesets (`*.json` with `columns`/`rows`/`tiles`): adds `frames` = trimmed rect per named tile.

Usage: uv run --no-project --with pillow python scripts/assets/build_sprite_manifests.py
"""

import json
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parents[2] / "assets"
ALPHA_THRESHOLD = 16


def opaque_box(image: Image.Image) -> tuple[int, int, int, int]:
    box = image.getchannel("A").point(lambda v: 255 if v > ALPHA_THRESHOLD else 0).getbbox()
    if box is None:
        raise ValueError("fully transparent image")
    return box


def rect(box: tuple[int, int, int, int], dx: int = 0, dy: int = 0) -> dict[str, int]:
    return {"x": box[0] + dx, "y": box[1] + dy, "w": box[2] - box[0], "h": box[3] - box[1]}


def build_items(path: Path) -> None:
    items = json.loads(path.read_text(encoding="utf-8"))
    for key, spec in items.items():
        texture = path.parent / spec["texture"]
        if not texture.exists():
            print(f"skip {key}: {texture.name} missing")
            continue
        spec["bounds"] = rect(opaque_box(Image.open(texture).convert("RGBA")))
    path.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    print(f"updated {path.relative_to(ASSETS)}")


def build_tileset(path: Path) -> None:
    spec = json.loads(path.read_text(encoding="utf-8"))
    sheet = Image.open(path.parent / spec["texture"]).convert("RGBA")
    cw, ch = sheet.width // spec["columns"], sheet.height // spec["rows"]
    frames = {}
    for i, name in enumerate(spec["tiles"]):
        x, y = (i % spec["columns"]) * cw, (i // spec["columns"]) * ch
        frames[name] = rect(opaque_box(sheet.crop((x, y, x + cw, y + ch))), x, y)
    spec["frames"] = frames
    path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(f"updated {path.relative_to(ASSETS)}")


def main() -> None:
    build_items(ASSETS / "gameplay" / "items.json")
    for tileset in (ASSETS / "environment" / "tiles").rglob("*.json"):
        build_tileset(tileset)


if __name__ == "__main__":
    main()
