"""End-to-end demo for Phase 1 of the applied AI system."""

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from src.assistant import MusicAIAssistant
from src.recommender import load_songs


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

SAMPLE_REQUESTS = [
    "I want happy pop for a morning commute with high energy.",
    "Give me chill acoustic music from the 2010s for studying.",
    "I need intense workout music with high energy.",
]


def _print_recommendations(request_name: str, recs) -> None:
    print(f"\n{'=' * 70}")
    print(f"  Request: {request_name}")
    print(f"{'=' * 70}")

    if HAS_TABULATE:
        rows = []
        for rank, (song, score, explanation) in enumerate(recs, 1):
            rows.append(
                [
                    rank,
                    song["title"],
                    song["artist"],
                    song["genre"],
                    song["mood"],
                    f"{song['energy']:.2f}",
                    f"{score:.3f}",
                    explanation,
                ]
            )
        headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score", "Reasons"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        for rank, (song, score, explanation) in enumerate(recs, 1):
            print(f"  {rank}. {song['title']} by {song['artist']}")
            print(f"     Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']:.2f}")
            print(f"     Score: {score:.3f}")
            print(f"     Because: {explanation}")
            print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    assistant = MusicAIAssistant(songs)
    print(f"Loaded songs: {len(songs)}")

    for request in SAMPLE_REQUESTS:
        result = assistant.answer_query(request, k=3)
        recs = [(item["song"], item["score"], item["explanation"]) for item in result["recommendations"]]
        _print_recommendations(request, recs)
        print(f"\nAI response: {result['response']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Guardrail passed: {result['guardrail_report']['passed']}")
        for check in result["guardrail_report"]["checks"]:
            print(f"  - {check}")


if __name__ == "__main__":
    main()
