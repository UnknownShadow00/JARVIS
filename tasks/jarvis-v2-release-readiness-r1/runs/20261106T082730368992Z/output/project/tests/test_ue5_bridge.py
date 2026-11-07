from app.comms.ue5_bridge import build_emotion_event, parse_emotion_from_reply


def test_build_emotion_neutral() -> None:
    result = build_emotion_event("neutral")
    assert result["animation"] == "Idle_01"


def test_build_emotion_success() -> None:
    result = build_emotion_event("success", 0.8)
    assert result["animation"] == "React_Happy"
    assert result["intensity"] == 0.8


def test_parse_emotion_found() -> None:
    result = parse_emotion_from_reply("Done, sir. [EMOTION:success]")
    assert result == "success"


def test_parse_emotion_missing() -> None:
    result = parse_emotion_from_reply("Right away, sir.")
    assert result is None
