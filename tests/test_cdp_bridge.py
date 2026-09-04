import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "chatgpt_cdp_bridge.py"
spec = importlib.util.spec_from_file_location("chatgpt_cdp_bridge", MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class HostMatchingTests(unittest.TestCase):
    def test_exact_host_matches(self):
        self.assertTrue(bridge._host_matches("https://chatgpt.com/c/123", "chatgpt.com"))

    def test_subdomain_matches(self):
        self.assertTrue(bridge._host_matches("https://www.chatgpt.com/", "chatgpt.com"))

    def test_substring_attack_does_not_match(self):
        self.assertFalse(
            bridge._host_matches("https://chatgpt.com.attacker.example/", "chatgpt.com")
        )

    def test_non_http_scheme_does_not_match(self):
        self.assertFalse(bridge._host_matches("chrome-extension://chatgpt.com/x", "chatgpt.com"))

    def test_select_target_tab_never_falls_back(self):
        tabs = [
            {"type": "page", "url": "https://mail.google.com/", "title": "Mail"},
            {"type": "page", "url": "https://github.com/", "title": "GitHub"},
        ]
        self.assertIsNone(bridge._select_target_tab(tabs, "chatgpt.com"))

    def test_select_target_tab_returns_expected_host(self):
        tabs = [
            {"type": "page", "url": "https://github.com/", "title": "GitHub"},
            {
                "type": "page",
                "url": "https://chatgpt.com/c/abc",
                "title": "ChatGPT",
                "webSocketDebuggerUrl": "ws://127.0.0.1/test",
            },
        ]
        selected = bridge._select_target_tab(tabs, "chatgpt.com")
        self.assertEqual(selected["title"], "ChatGPT")


class ResponseIdentityTests(unittest.TestCase):
    def test_same_old_response_is_not_new(self):
        initial = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "old"}
        current = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "old"}
        self.assertFalse(bridge._is_new_response(initial, current))

    def test_higher_message_count_is_new(self):
        initial = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "old"}
        current = {"assistantCount": 4, "lastIdentity": "m4", "lastText": "new"}
        self.assertTrue(bridge._is_new_response(initial, current))

    def test_changed_identity_is_new(self):
        initial = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "old"}
        current = {"assistantCount": 3, "lastIdentity": "m4", "lastText": "old"}
        self.assertTrue(bridge._is_new_response(initial, current))

    def test_changed_text_is_new(self):
        initial = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "old"}
        current = {"assistantCount": 3, "lastIdentity": "m3", "lastText": "new"}
        self.assertTrue(bridge._is_new_response(initial, current))


if __name__ == "__main__":
    unittest.main()
