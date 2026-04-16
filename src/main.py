"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for multiple distinct user profiles and displays
results in a formatted table.  Demonstrates standard mode plus the
three alternative ranking modes (genre_first, mood_first, energy_first).
"""

import sys
import os

# Allow running as `python -m src.main` from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# User profiles (Phase 4 – at least 3 distinct profiles required by rubric)
# ---------------------------------------------------------------------------
PROFILES = {
    "Happy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "valence": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
        "likes_acoustic": True,
    },
    "High-Energy EDM Gym": {
        "genre": "electronic",
        "mood": "intense",
        "energy": 0.95,
        "valence": 0.50,
        "likes_acoustic": False,
    },
    "Acoustic Folk Wanderer": {
        "genre": "folk",
        "mood": "chill",
        "energy": 0.30,
        "valence": 0.72,
        "likes_acoustic": True,
    },
    "Moody Indie Night Owl": {
        "genre": "indie pop",
        "mood": "moody",
        "energy": 0.65,
        "valence": 0.42,
        "likes_acoustic": False,
    },
}

# Experiment profile used in Phase 4 Step 3 (energy-doubled, genre-halved)
EXPERIMENT_PROFILE = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.80,
    "valence": 0.85,
    "likes_acoustic": False,
}


def _print_recommendations(profile_name: str, recs, k: int) -> None:
    """Pretty-prints a recommendation list using tabulate (or plain text)."""
    print(f"\n{'='*70}")
    print(f"  Profile: {profile_name}")
    print(f"{'='*70}")

    if HAS_TABULATE:
        rows = []
        for rank, (song, score, explanation) in enumerate(recs, 1):
            rows.append([
                rank,
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                f"{song['energy']:.2f}",
                f"{score:.3f}",
                explanation,
            ])
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
    print(f"Loaded songs: {len(songs)}")

    k = 5

    # -----------------------------------------------------------------------
    # Standard recommendations for each profile
    # -----------------------------------------------------------------------
    for name, prefs in PROFILES.items():
        recs = recommend_songs(prefs, songs, k=k, mode="standard", diversity=True)
        _print_recommendations(name, recs, k)

    # -----------------------------------------------------------------------
    # Phase 4 Step 3: Data Experiment — Energy-First mode vs Standard mode
    # for the Happy Pop Fan profile (doubles energy weight, halves genre weight)
    # -----------------------------------------------------------------------
    print("\n" + "#"*70)
    print("  EXPERIMENT: 'Happy Pop Fan' — Standard vs Energy-First ranking")
    print("#"*70)

    std_recs = recommend_songs(EXPERIMENT_PROFILE, songs, k=k, mode="standard", diversity=False)
    _print_recommendations("Happy Pop Fan [standard mode]", std_recs, k)

    energy_recs = recommend_songs(EXPERIMENT_PROFILE, songs, k=k, mode="energy_first", diversity=False)
    _print_recommendations("Happy Pop Fan [energy_first mode]", energy_recs, k)

    # -----------------------------------------------------------------------
    # Bonus: show all four ranking modes for the High-Energy EDM profile
    # -----------------------------------------------------------------------
    print("\n" + "#"*70)
    print("  BONUS: All 4 ranking modes for 'High-Energy EDM Gym'")
    print("#"*70)
    edm_prefs = PROFILES["High-Energy EDM Gym"]
    for mode in ["standard", "genre_first", "mood_first", "energy_first"]:
        recs = recommend_songs(edm_prefs, songs, k=3, mode=mode, diversity=False)
        _print_recommendations(f"High-Energy EDM Gym [{mode}]", recs, 3)


if __name__ == "__main__":
    main()
