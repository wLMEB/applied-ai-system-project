import csv
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ranking mode weight tables (stretch: multiple ranking strategies)
# ---------------------------------------------------------------------------
RANKING_MODES: Dict[str, Dict[str, float]] = {
    "standard":    {"genre": 2.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5, "valence": 0.5},
    "genre_first": {"genre": 4.0, "mood": 0.5, "energy": 0.5, "acoustic": 0.3, "valence": 0.3},
    "mood_first":  {"genre": 1.0, "mood": 3.0, "energy": 0.5, "acoustic": 0.3, "valence": 0.5},
    "energy_first":{"genre": 0.5, "mood": 0.5, "energy": 3.0, "acoustic": 0.3, "valence": 0.3},
}


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Extended attributes added in Phase 2 (have defaults for test compatibility)
    popularity: int = 50
    release_decade: str = "2020s"
    instrumentalness: float = 0.0
    speechiness: float = 0.05
    liveness: float = 0.1


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.6
    preferred_decade: str = ""


class Recommender:
    """OOP wrapper around the recommendation logic (required by tests)."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _to_dict(self, song: Song) -> Dict:
        """Convert Song dataclass to the dict format expected by score_song."""
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "popularity": song.popularity,
            "release_decade": song.release_decade,
            "instrumentalness": song.instrumentalness,
            "speechiness": song.speechiness,
            "liveness": song.liveness,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns top k songs ranked by score for the given user profile."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "valence": user.target_valence,
        }
        scored = []
        for song in self.songs:
            score, _ = score_song(user_prefs, self._to_dict(song))
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation for why this song was recommended."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "valence": user.target_valence,
        }
        _, reasons = score_song(user_prefs, self._to_dict(song))
        return "; ".join(reasons) if reasons else "No strong feature match found"


# ---------------------------------------------------------------------------
# Functional API (used by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file and returns a list of dicts with proper types."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "popularity":       int(row.get("popularity", 50)),
                "release_decade":   row.get("release_decade", "2020s"),
                "instrumentalness": float(row.get("instrumentalness", 0.0)),
                "speechiness":      float(row.get("speechiness", 0.05)),
                "liveness":         float(row.get("liveness", 0.1)),
            })
    LOGGER.info("Loaded songs", extra={"csv_path": csv_path, "song_count": len(songs)})
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    mode: str = "standard",
) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.

    Returns (score, reasons) where reasons is a list of human-readable strings
    explaining each point contribution.
    """
    weights = RANKING_MODES.get(mode, RANKING_MODES["standard"])
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song.get("genre") == user_prefs.get("genre"):
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match (+{pts:.1f})")

    # Mood match
    if song.get("mood") == user_prefs.get("mood"):
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match (+{pts:.1f})")

    # Energy similarity (proximity reward — closer = more points)
    target_energy = user_prefs.get("energy", 0.5)
    energy_sim = max(0.0, 1.0 - abs(song["energy"] - target_energy))
    energy_pts = round(energy_sim * weights["energy"], 2)
    score += energy_pts
    if energy_pts >= weights["energy"] * 0.75:
        reasons.append(f"close energy match (+{energy_pts:.2f})")

    # Acousticness match (only when user prefers acoustic)
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        pts = weights["acoustic"]
        score += pts
        reasons.append(f"acoustic feel (+{pts:.1f})")

    # Valence (emotional positivity) similarity
    target_valence = user_prefs.get("valence", 0.6)
    valence_sim = max(0.0, 1.0 - abs(song["valence"] - target_valence))
    valence_pts = round(valence_sim * weights["valence"], 2)
    score += valence_pts
    if valence_pts >= weights["valence"] * 0.75:
        reasons.append(f"matching vibe/valence (+{valence_pts:.2f})")

    return round(score, 3), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "standard",
    diversity: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """
    Returns the top k song recommendations sorted by score (highest first).

    Each result is a tuple of (song_dict, score, explanation_string).

    When diversity=True an artist-diversity penalty is applied so the same
    artist cannot dominate the top-k list (stretch: fairness/anti-filter-bubble).
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")
    if not songs:
        raise ValueError("songs must not be empty")

    # Score every song
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = "; ".join(reasons) if reasons else "no strong match"
        scored.append((song, score, explanation))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    if not diversity:
        return scored[:k]

    # Artist-diversity pass: penalise a song by 1.0 if its artist already
    # appears in the selected list.  This prevents one artist dominating the
    # entire recommendation.
    selected: List[Tuple[Dict, float, str]] = []
    seen_artists: Dict[str, int] = {}

    for song, score, explanation in scored:
        artist = song.get("artist", "")
        appearances = seen_artists.get(artist, 0)
        if appearances >= 1:
            adjusted_score = score - 1.0 * appearances
            explanation = explanation + f" [artist diversity penalty: -{1.0 * appearances:.1f}]"
        else:
            adjusted_score = score
        selected.append((song, round(adjusted_score, 3), explanation))
        seen_artists[artist] = appearances + 1

    # Re-sort after penalty adjustments
    selected.sort(key=lambda x: x[1], reverse=True)
    LOGGER.info(
        "Generated recommendations",
        extra={"mode": mode, "k": k, "diversity": diversity, "candidate_count": len(selected)},
    )
    return selected[:k]
