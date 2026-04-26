from src.assistant import MusicAIAssistant
from src.recommender import load_songs


def make_assistant() -> MusicAIAssistant:
    return MusicAIAssistant(load_songs("data/songs.csv"))


def test_parse_request_detects_music_preferences():
    assistant = make_assistant()

    parsed = assistant.parse_request("Play happy pop songs with high energy")

    assert parsed.user_prefs["genre"] == "pop"
    assert parsed.user_prefs["mood"] == "happy"
    assert parsed.user_prefs["energy"] >= 0.9
    assert parsed.confidence > 0.5


def test_answer_query_returns_grounded_results():
    assistant = make_assistant()

    result = assistant.answer_query("Give me chill acoustic songs from the 2010s", k=2)

    assert len(result["recommendations"]) == 2
    assert "catalog evidence" in result["response"].lower()
    assert result["recommendations"][0]["song"]["title"]
    assert result["guardrail_report"]["passed"] is True


def test_short_ambiguous_query_creates_guardrail_warning():
    assistant = make_assistant()

    result = assistant.answer_query("music", k=2)

    assert result["parsed_request"].warnings
    assert "guardrail note" in result["response"].lower()
