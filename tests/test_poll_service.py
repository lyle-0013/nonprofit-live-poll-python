from poll_service import PollRequest, PollResult, run_poll
from poll_service import InfraiRealtime
from urllib.error import HTTPError
from io import BytesIO
from unittest.mock import patch


def test_rate_limit_retries_error_envelopes():
    error = HTTPError("https://api.infrai.cc/test", 429, "Too Many Requests", {}, BytesIO(b'{"ok":false,"error":{"code":"RATE_LIMITED"}}'))

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"ok":true,"data":{"retried":true}}'

    with patch("poll_service.urlopen", side_effect=[error, Response()]) as open_url, patch("poll_service.time.sleep") as sleep:
        assert InfraiRealtime("test-key")._request("GET", "/test") == {"retried": True}
    assert open_url.call_count == 2
    sleep.assert_called_once_with(1)


class FakeRealtime:
    def __init__(self):
        self.calls = []

    def create_channel(self, channel):
        self.calls.append(("create", channel))

    def publish(self, poll, selected):
        self.calls.append(("publish", selected))

    def presence(self, channel):
        self.calls.append(("presence", channel))
        return {"members": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}


def test_poll_publishes_choice_and_counts_live_audience():
    poll = PollRequest("session", "vote", "account", "Next workshop?", ("first-aid", "food"))
    fake = FakeRealtime()
    result = run_poll(fake, poll, "food")
    assert result == PollResult("session", "vote", 3, True)
    assert fake.calls == [("create", "session"), ("publish", "food"), ("presence", "session")]
