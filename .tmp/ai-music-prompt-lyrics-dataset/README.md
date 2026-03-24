# AI Music Prompt & Lyrics Dataset (Suno + Udio)

This starter dataset provides structured examples for high-intensity AI music generation workflows.

## Files

- `music_prompts_lyrics.jsonl`: one JSON object per track concept with prompt structure, dedicated `suno_prompt` text, musical attributes, and original lyrics
- `schema.json`: field definitions for the JSONL records

## Intended uses

- Prompt engineering for music generation systems
- Fine-tuning or retrieval-augmented prompt selection
- Evaluation of style, structure, and lyrical consistency across genres
- Short-form Suno prompt generation with reusable style descriptors

## Notes

- All lyrics in this dataset are original sample content.
- The data emphasizes deathcore, trap, drill, hybrid metal, and experimental electronic styles.
- Prompt text is formatted to be directly reusable in generation pipelines.
- `suno_prompt` is intentionally shorter and style-focused than the general `prompt` field.
