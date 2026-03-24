from safe_lyrics.trend_analyzer import build_trend_index, load_platform_signals, write_trend_index


def main() -> int:
    signals = load_platform_signals()
    index = build_trend_index(signals)
    write_trend_index(index)
    print(f"Indexed {index['source_count']} platform signals into data/trend_index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
