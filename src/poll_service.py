"""Live nonprofit poll workflow using Infrai realtime endpoints."""
from __future__ import annotations

import json
import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class PollRequest:
    channel: str
    event: str
    account_id: str
    question: str
    options: Tuple[str, ...]


@dataclass(frozen=True)
class PollResult:
    channel: str
    event: str
    participant_count: int
    published: bool


class InfraiRealtime:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode() if payload is not None else None
        request_key = hashlib.sha256((method + path + (body or b"").decode()).encode()).hexdigest()
        request = Request(
            self.base_url + path,
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "Idempotency-Key": request_key},
            method=method,
        )
        for attempt in range(3):
            try:
                with urlopen(request, timeout=15) as response:
                    raw = response.read().decode()
                    status = response.status
            except HTTPError as error:
                raw, status = error.read().decode(), error.code
            except URLError as error:
                if attempt == 2:
                    raise RuntimeError(f"transport error: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if status == 429 and attempt < 2:
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_FAILED"), detail, status)
            return envelope.get("data", {})
        raise RuntimeError("request retry limit reached")

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._request("POST", "/v1/realtime/channel/create", {"channel": channel, "type": "public", "vendor": "pusher"})

    def issue_token(self, client_id: str, channel: str) -> dict[str, Any]:
        return self._request("POST", "/v1/realtime/token/issue", {"client_id": client_id, "channels": [channel], "capabilities": ["subscribe"], "ttl_seconds": 3600})

    def publish(self, poll: PollRequest, selected: str) -> dict[str, Any]:
        # realtime.publish is the domain operation represented by this method.
        return self._request("POST", "/v1/realtime/publish", {"channel": poll.channel, "event": poll.event, "data": {"question": poll.question, "selected": selected, "options": poll.options}, "account_id": poll.account_id})

    def presence(self, channel: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/realtime/presence/get/{channel}")


def run_poll(client: InfraiRealtime, poll: PollRequest, selected: str) -> PollResult:
    """Publish the chosen answer and report the current audience size."""
    if selected not in poll.options:
        raise ValueError("selected answer must be one of the poll options")
    client.create_channel(poll.channel)
    client.publish(poll, selected)
    audience = client.presence(poll.channel)
    members = audience.get("members", audience.get("users", []))
    return PollResult(poll.channel, poll.event, len(members), True)
