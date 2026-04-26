"""AI playlist assistant built on top of the recommender."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.recommender import recommend_songs


LOGGER = logging.getLogger(__name__)

ENERGY_HINTS = {
    "high": 0.9,
    "energetic": 0.9,
    "hype": 0.92,
    "workout": 0.95,
    "gym": 0.95,
    "dance": 0.85,
    "medium": 0.6,
    "balanced": 0.6,
    "low": 0.35,
    "calm": 0.3,
    "quiet": 0.25,
    "sleep": 0.2,
}

VALENCE_HINTS = {
    "happy": 0.85,
    "uplifting": 0.82,
    "positive": 0.8,
    "chill": 0.6,
    "relaxed": 0.68,
    "moody": 0.4,
    "sad": 0.25,
    "melancholy": 0.2,
    "intense": 0.45,
}

ACOUSTIC_HINTS = {"acoustic", "organic", "unplugged", "folky"}


@dataclass
class ParsedRequest:
    """Structured interpretation of a user request."""

    raw_query: str
    user_prefs: Dict
    detected_terms: List[str]
    confidence: float
    warnings: List[str]


class MusicAIAssistant:
    """Retrieval-based assistant grounded in the local song catalog."""

    def __init__(self, songs: List[Dict]):
        if not songs:
            raise ValueError("MusicAIAssistant requires at least one song")
        self.songs = songs
        self.available_genres = sorted({song["genre"] for song in songs})
        self.available_moods = sorted({song["mood"] for song in songs})
        self.available_decades = sorted(
            {song.get("release_decade", "") for song in songs if song.get("release_decade")}
        )

    def parse_request(self, query: str) -> ParsedRequest:
        """Infer a user preference profile from a free-form request."""
        if not query or not query.strip():
            raise ValueError("Query must not be empty")

        normalized = query.lower()
        detected_terms: List[str] = []
        warnings: List[str] = []

        genre = self._find_term(normalized, self.available_genres)
        if genre:
            detected_terms.append(f"genre:{genre}")

        mood = self._find_term(normalized, self.available_moods)
        if mood:
            detected_terms.append(f"mood:{mood}")

        decade = self._find_term(normalized, self.available_decades)
        if decade:
            detected_terms.append(f"decade:{decade}")

        energy = self._match_weighted_hint(normalized, ENERGY_HINTS, default=0.55)
        valence = self._match_weighted_hint(normalized, VALENCE_HINTS, default=0.6)
        likes_acoustic = any(word in normalized for word in ACOUSTIC_HINTS)

        if likes_acoustic:
            detected_terms.append("preference:acoustic")

        user_prefs = {
            "genre": genre or "",
            "mood": mood or "",
            "energy": energy,
            "valence": valence,
            "likes_acoustic": likes_acoustic,
            "preferred_decade": decade or "",
        }

        if not genre and not mood:
            warnings.append("No genre or mood was detected, so the assistant used broad defaults.")
        if len(query.split()) < 3:
            warnings.append("The request is very short, so recommendation confidence is limited.")

        confidence = min(1.0, 0.25 + 0.15 * len(detected_terms) + (0.15 if genre or mood else 0.0))
        LOGGER.info("Parsed user request", extra={"query": query, "confidence": round(confidence, 2)})
        return ParsedRequest(query, user_prefs, detected_terms, round(confidence, 2), warnings)

    def answer_query(self, query: str, k: int = 3) -> Dict:
        """Retrieve relevant songs and generate a grounded response."""
        parsed = self.parse_request(query)
        candidates = self._retrieve_candidates(parsed, k=max(k, 5))
        top_results = candidates[:k]
        guardrail_report = self._guardrail_check(parsed, top_results)
        response = self._build_response(parsed, top_results)
        return {
            "query": query,
            "parsed_request": parsed,
            "recommendations": top_results,
            "response": response,
            "confidence": parsed.confidence,
            "guardrail_report": guardrail_report,
        }

    def _retrieve_candidates(self, parsed: ParsedRequest, k: int) -> List[Dict]:
        ranked = recommend_songs(parsed.user_prefs, self.songs, k=len(self.songs), diversity=True)
        preferred_decade = parsed.user_prefs.get("preferred_decade", "")

        filtered: List[Dict] = []
        for song, score, explanation in ranked:
            retrieval_bonus = 0.0
            if preferred_decade and song.get("release_decade") == preferred_decade:
                retrieval_bonus += 0.35
                explanation = f"{explanation}; decade match (+0.35)"
            filtered.append(
                {
                    "song": song,
                    "score": round(score + retrieval_bonus, 3),
                    "explanation": explanation,
                }
            )

        filtered.sort(key=lambda item: item["score"], reverse=True)
        LOGGER.info("Retrieved candidates", extra={"query": parsed.raw_query, "count": len(filtered)})
        return filtered[:k]

    def _build_response(self, parsed: ParsedRequest, results: List[Dict]) -> str:
        if not results:
            return "I could not find a recommendation from the current song catalog."

        lead = results[0]["song"]
        reason = results[0]["explanation"]
        lines = [
            f"Based on your request, I would start with '{lead['title']}' by {lead['artist']}.",
            f"It stands out because it fits the catalog evidence: {reason}.",
        ]

        if len(results) > 1:
            backups = ", ".join(f"{item['song']['title']} by {item['song']['artist']}" for item in results[1:])
            lines.append(f"Good backup options from the retrieved matches are {backups}.")

        if parsed.detected_terms:
            lines.append(f"I interpreted your request using these signals: {', '.join(parsed.detected_terms)}.")
        else:
            lines.append("I used a general preference profile because the request did not include many specific cues.")

        if parsed.warnings:
            lines.append(f"Guardrail note: {' '.join(parsed.warnings)}")

        return " ".join(lines)

    def _guardrail_check(self, parsed: ParsedRequest, results: List[Dict]) -> Dict:
        """Verify the retrieved output remains grounded in the interpreted request."""
        checks: List[str] = []
        passed = True

        if not results:
            return {"passed": False, "checks": ["No results returned from retrieval."]}

        requested_decade = parsed.user_prefs.get("preferred_decade", "")
        if requested_decade:
            matching = [item for item in results if item["song"].get("release_decade") == requested_decade]
            if matching:
                checks.append(f"At least one retrieved song matches the requested decade {requested_decade}.")
            else:
                passed = False
                checks.append(f"No retrieved song matched the requested decade {requested_decade}.")

        if parsed.user_prefs.get("genre"):
            checks.append(f"Genre signal '{parsed.user_prefs['genre']}' was used during retrieval.")
        if parsed.user_prefs.get("mood"):
            checks.append(f"Mood signal '{parsed.user_prefs['mood']}' was used during retrieval.")
        if parsed.warnings:
            checks.extend(parsed.warnings)

        return {"passed": passed, "checks": checks}

    @staticmethod
    def _find_term(text: str, options: List[str]) -> Optional[str]:
        for option in options:
            pattern = r"\b" + re.escape(option.lower()) + r"\b"
            if re.search(pattern, text):
                return option
        return None

    @staticmethod
    def _match_weighted_hint(text: str, hint_map: Dict[str, float], default: float) -> float:
        for hint, value in hint_map.items():
            if hint in text:
                return value
        return default
