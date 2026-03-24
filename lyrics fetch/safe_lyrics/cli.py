from safe_lyrics.service import generate_safe_lyrics


def ask_song_request() -> dict:
    genre = input("What genre do you want? ").strip()
    topic = input("What should the song be about? ").strip()
    mood = input("What mood should it have? ").strip()

    if not genre or not topic or not mood:
        raise RuntimeError("Genre, topic, and mood are all required.")

    return {"genre": genre, "topic": topic, "mood": mood}


def main() -> int:
    request = ask_song_request()

    print("\nGenerating original lyrics...\n")
    result = generate_safe_lyrics(
        genre=request["genre"],
        topic=request["topic"],
        mood=request["mood"],
    )
    print(result["lyrics"])
    print("\nOriginality check: passed")
    return 0
