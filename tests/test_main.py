"""Run from the repository root with:  python -m unittest discover tests -v"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main  # noqa: E402


class ChatTests(unittest.TestCase):
    def setUp(self):
        main.messages.clear()
        self.client = main.app.test_client()

    def send(self, **body):
        return self.client.post("/send", json=body)

    def test_send_and_list(self):
        self.assertEqual(self.send(name="Anna", text="Hallo", timer=0).status_code, 200)
        data = self.client.get("/messages").get_json()
        self.assertEqual(data, [{"name": "Anna", "text": "Hallo", "left": "Permanent Message"}])

    def test_timed_message_shows_time_left(self):
        self.send(name="Anna", text="Hi", timer=30)
        left = self.client.get("/messages").get_json()[0]["left"]
        self.assertRegex(left, r"Disappears in (29|30)s")

    def test_expired_messages_are_removed(self):
        self.send(name="Anna", text="Bye", timer=10)
        later = datetime.now(timezone.utc) + timedelta(seconds=11)
        with patch.object(main, "datetime") as fake:
            fake.now.return_value = later
            self.assertEqual(self.client.get("/messages").get_json(), [])

    def test_invalid_requests_rejected(self):
        cases = [
            {"name": "", "text": "x", "timer": 0},
            {"name": "Anna", "text": "   ", "timer": 0},
            {"name": "Anna", "text": "x", "timer": 999},
            {"name": "Anna", "text": "x", "timer": "abc"},
            {"name": "A" * 31, "text": "x", "timer": 0},
            {"name": "Anna", "text": "x" * 501, "timer": 0},
        ]
        for body in cases:
            with self.subTest(body=body):
                self.assertEqual(self.send(**body).status_code, 400)
        self.assertEqual(main.messages, [])

    def test_non_json_body_rejected(self):
        response = self.client.post("/send", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)

    def test_message_count_is_capped(self):
        for i in range(main.MAX_MESSAGES + 5):
            self.send(name="Bot", text=str(i), timer=0)
        data = self.client.get("/messages").get_json()
        self.assertEqual(len(data), main.MAX_MESSAGES)
        self.assertEqual(data[-1]["text"], str(main.MAX_MESSAGES + 4))  # newest kept

    def test_page_renders_messages_as_text(self):
        page = self.client.get("/").get_data(as_text=True)
        self.assertIn("textContent", page)
        self.assertNotIn("box.innerHTML +=", page)


if __name__ == "__main__":
    unittest.main()
