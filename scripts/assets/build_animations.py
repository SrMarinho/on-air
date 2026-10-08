"""Fill geometry fields of a character's animations.json from its spritesheets.

Authors own timing (`frames`, `columns`, `duration`, `loop`, `next`). This script adds
`frameWidth`, `frameHeight`, `scale` (normalizes character height to `idle`) and `anchor`
(feet position inside the frame). Sheets that do not exist yet are left untouched.

Usage: uv run --no-project --with pillow python scripts/assets/build_animations.py assets/characters/calouro
"""

import json
import statistics
import sys
from pathlib import Path

from PIL import Image

ALPHA_THRESHOLD = 16
REFERENCE = "idle"


def frame_boxes(sheet: Image.Image, frames: int, columns: int) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    rows = -(-frames // columns)
    fw, fh = sheet.width // columns, sheet.height // rows
    alpha = sheet.getchannel("A").point(lambda v: 255 if v > ALPHA_THRESHOLD else 0)
    boxes = []
    for i in range(frames):
        x, y = (i % columns) * fw, (i // columns) * fh
        box = alpha.crop((x, y, x + fw, y + fh)).getbbox()
        if box:
            boxes.append(box)
    return fw, fh, boxes


def main(character_dir: Path) -> None:
    path = character_dir / "data" / "animations.json"
    animations: dict[str, dict] = json.loads(path.read_text(encoding="utf-8"))
    measured: dict[str, float] = {}
    for name, spec in animations.items():
        sheet_path = character_dir / "sprites" / spec["texture"]
        if not sheet_path.exists():
            print(f"skip {name}: {sheet_path.name} missing")
            continue
        fw, fh, boxes = frame_boxes(Image.open(sheet_path).convert("RGBA"), spec["frames"], spec["columns"])
        spec["frameWidth"], spec["frameHeight"] = fw, fh
        spec["anchor"] = {
            "x": round(statistics.median((b[0] + b[2]) / 2 / fw for b in boxes), 3),
            "y": round(max(b[3] for b in boxes) / fh, 3),
        }
        measured[name] = statistics.median(b[3] - b[1] for b in boxes)
    reference = measured[REFERENCE]
    for name, height in measured.items():
        animations[name]["scale"] = round(reference / height, 4)
    animations[REFERENCE]["referenceHeight"] = reference
    path.write_text(json.dumps(animations, indent=2) + "\n", encoding="utf-8")
    print(f"updated {path}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
