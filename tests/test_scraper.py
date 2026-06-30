from src.scraper import extract_message


class DummyMessage:
    def __init__(self):
        self.id = 1
        self.date = __import__("datetime").datetime(2026, 1, 1)
        self.message = "Test message"
        self.media = None
        self.views = None
        self.forwards = None


def test_extract_message_returns_expected_keys():
    msg = DummyMessage()

    result = extract_message(msg, "TestChannel")

    expected_keys = {
        "message_id",
        "channel_name",
        "message_date",
        "message_text",
        "has_media",
        "image_path",
        "views",
        "forwards",
    }

    assert set(result.keys()) == expected_keys
    assert result["views"] == 0
    assert result["forwards"] == 0
    