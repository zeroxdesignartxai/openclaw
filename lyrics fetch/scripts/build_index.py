import json
from pathlib import Path

from safe_lyrics.style_indexer import build_style_index

SOURCE_PATH = Path("data/source_lyrics.json")
OUTPUT_PATH = Path("data/style_index.json")


def main() -> int:
    entries = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("data/source_lyrics.json must contain at least one source entry.")

    style_index = build_style_index(entries)
    OUTPUT_PATH.write_text(f"{json.dumps(style_index, indent=2)}\n", encoding="utf-8")
    print(f"Indexed {style_index['source_count']} source lyrics into {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
