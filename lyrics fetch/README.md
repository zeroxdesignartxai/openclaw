# Safe Lyrics Studio

`Safe Lyrics Studio` is a small Python CLI app that helps generate original lyrics while reducing the risk of copying copyrighted text.

## What it does

- Asks the user what genre they want
- Asks what the song is about
- Builds style guidance from source lyrics without sending raw lyrics to the model
- Builds safe trend guidance from platform metadata instead of copying songs
- Blocks outputs that are too similar to indexed source material

## Safety model

The app is designed around a strict rule:

- Source lyrics are analyzed into abstract style features only
- Raw source lyrics are never inserted into the generation prompt
- Generated output is checked against the indexed corpus before it is accepted

This reduces risk, but it is not a legal guarantee. Human review is still recommended before publication.

## Setup

1. Use Python 3.12 or newer.
2. Put source material into `data/source_lyrics.json`.
3. Build the safe style index:

```bash
python scripts/build_index.py
```

4. Build the trend index:

```bash
python scripts/build_trend_index.py
```

5. Set an API key if you want live AI generation.
6. Start the CLI:

```bash
python app.py
```

7. Or launch the web app:

```bash
python app.py serve
```

Then open `http://127.0.0.1:8000`.

## Source data format

`data/source_lyrics.json`:

```json
[
  {
    "id": "song-1",
    "title": "Example Song",
    "artist": "Example Artist",
    "genre": "Pop",
    "lyrics": "Full lyrics text here"
  }
]
```

## Environment variables

- `OPENAI_API_KEY`: required for live generation
- `OPENAI_MODEL`: optional, defaults to `gpt-4.1-mini`
- `OPENAI_BASE_URL`: optional, defaults to `https://api.openai.com/v1`
- `GEMINI_API_KEY`: optional alternative provider key
- `GEMINI_MODEL`: optional, defaults to `gemini-2.0-flash`

## API endpoints

- `GET /api/health`
- `GET /api/trends?genre=pop`
- `POST /api/generate`
- `POST /api/format`

## Testing

```bash
python -m unittest discover -s tests
```

## Notes

- The app rejects generation when similarity checks fail.
- The source corpus stays local.
- You can replace the sample dataset with your own licensed or permitted dataset.
