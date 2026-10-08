"""Slice the authored UI sheets in assets/ui/sheets into individual sprites.

Usage: uv run --no-project --with pillow --with numpy --with scipy python scripts/assets/build_ui.py
"""

import json
from pathlib import Path

from slice_sheet import slice_sheet

ASSETS = Path(__file__).resolve().parents[2] / "assets"

# Element names in reading order (row by row, left to right) for each sheet.
SHEETS: dict[str, list[str]] = {
    "ui-kit.png": [
        "buttons/button-primary", "buttons/button-secondary", "buttons/button-highlight",
        "buttons/button-danger",
        "controls/input-text", "controls/input-code", "controls/toggle-off", "controls/toggle-on",
        "controls/slider", "controls/tabs", "controls/chip-ready", "controls/chip-waiting",
        "cards/panel", "cards/item-card", "cards/toast", "cards/modal-confirm",
    ],
    "hud-kit.png": [
        "hud/on-air-sign", "hud/timer", "hud/round-badge", "hud/pause-button",
        "hud/player-plate-1", "hud/player-plate-2", "hud/player-plate-3", "hud/player-plate-4",
        "hud/nameplate-world", "hud/leader-crown", "hud/offscreen-arrow", "hud/host-caption",
    ],
    "build-controls.png": [
        "cursors/placement-valid", "cursors/placement-invalid", "cursors/build-hand",
        "cursors/ghost-block",
        "@effects/telegraphs/path-horizontal", "@effects/telegraphs/path-vertical",
        "@effects/telegraphs/path-rotate", "@effects/telegraphs/blast-cross",
        "hud/build-timer", "hud/hint-rotate", "hud/hint-place", "hud/alert-viral-moment",
    ],
    "icons.png": [
        "icons/play", "icons/pause", "icons/settings", "icons/players", "icons/microphone",
        "icons/trophy",
        "icons/crown", "icons/timer", "icons/sound", "icons/mute", "icons/gamepad", "icons/key",
        "icons/copy", "icons/share", "icons/exit", "icons/check", "icons/close", "icons/back",
        "icons/star", "icons/gong", "icons/chat", "icons/replay", "icons/lock", "icons/offline",
    ],
}


# Icons have detached parts (dots, slashes) that must stay together.
MERGE_RADIUS = {"icons.png": 14}


def output_path(name: str) -> Path:
    # "@path" is relative to assets/, everything else to assets/ui/.
    return ASSETS / f"{name[1:]}.png" if name.startswith("@") else ASSETS / "ui" / f"{name}.png"


def main() -> None:
    manifest: dict[str, str] = {}
    for sheet, names in SHEETS.items():
        outputs = [output_path(n) for n in names]
        slice_sheet(ASSETS / "ui" / "sheets" / sheet, outputs, MERGE_RADIUS.get(sheet, 3))
        for name, out in zip(names, outputs, strict=True):
            manifest[name.lstrip("@").split("/")[-1]] = out.relative_to(ASSETS).as_posix()
        print(f"{sheet}: {len(outputs)} sprites")
    (ASSETS / "ui" / "ui.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
