"""Export the wire protocol as JSON Schema for the clients (web Zod, Godot reference)."""

import json
from pathlib import Path

from onair.protocol.client import client_message_adapter
from onair.protocol.server import server_message_adapter

OUT = Path(__file__).resolve().parents[2] / "shared" / "protocol"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, adapter in (("client", client_message_adapter), ("server", server_message_adapter)):
        schema = adapter.json_schema(mode="serialization")
        path = OUT / f"{name}-messages.schema.json"
        path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
