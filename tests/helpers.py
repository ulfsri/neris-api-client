from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from types import SimpleNamespace
from typing import Any

import requests

from neris_api_client.client import _NerisApiClient
from neris_api_client.config import GrantType, TokenSet


_MISSING = object()


class FakeResponse:
    """Small requests.Response stand-in for deterministic unit tests."""

    def __init__(
        self,
        payload: Any = _MISSING,
        *,
        status_code: int = 200,
        text: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.payload = payload
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def json(self) -> Any:
        if self.payload is _MISSING:
            raise requests.exceptions.JSONDecodeError(
                "No JSON object could be decoded", self.text, 0
            )

        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code < 400:
            return

        error = requests.HTTPError(f"{self.status_code} HTTP error")
        error.response = self
        raise error


class RecordingSession:
    """Record requests and return queued responses without network access."""

    def __init__(self, responses: Iterable[FakeResponse] = ()) -> None:
        self.headers: dict[str, str] = {}
        self.requests: list[tuple[str, str, dict[str, Any]]] = []
        self._responses = iter(responses)

    def _request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.requests.append((method, url, kwargs))

        try:
            return next(self._responses)
        except StopIteration as error:
            raise AssertionError(f"No fake response queued for {method.upper()} {url}") from error

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._request("get", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._request("post", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._request("put", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._request("patch", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> FakeResponse:
        return self._request("delete", url, **kwargs)


def make_client(
    responses: Iterable[FakeResponse] = (),
    *,
    validate: bool = False,
    authenticated: bool = True,
) -> tuple[_NerisApiClient, RecordingSession]:
    """Build a client without invoking its credential-validating constructor."""

    client = object.__new__(_NerisApiClient)
    client.config = SimpleNamespace(
        base_url="https://api.example.test/v1",
        debug=False,
        validate=validate,
        grant_type=GrantType.PASSWORD,
        username="user@example.test",
        password="secret",
    )
    client.tokens = TokenSet(
        access_token="access-token" if authenticated else "",
        refresh_token="refresh-token" if authenticated else "",
        expires_at=datetime.max if authenticated else datetime.min,
    )
    session = RecordingSession(responses)
    client._session = session

    return client, session
