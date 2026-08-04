from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import requests

from neris_api_client.client import _NerisApiClient
from neris_api_client.config import GrantType, TokenSet


class Response:
    headers = {}
    text = ""

    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} Client Error")
            error.response = self
            raise error

    def json(self):
        return self.payload


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def post(self, *args, **kwargs):
        self.requests.append((args, kwargs))
        return next(self.responses)


def client_for(responses):
    client = object.__new__(_NerisApiClient)
    client.config = SimpleNamespace(
        base_url="https://api.example.test",
        debug=False,
        grant_type=GrantType.PASSWORD,
        username="user@example.test",
        password="secret",
    )
    client.tokens = TokenSet(access_token="", refresh_token="", expires_at=datetime.min)
    client._session = Session(responses)
    return client


class TokenResponseTests(unittest.TestCase):
    def test_success_response_without_refresh_token_is_accepted(self):
        client = client_for([Response({"access_token": "token", "expires_in": 3600})])

        client._update_auth()

        self.assertEqual(client.tokens.access_token, "token")
        self.assertEqual(client.tokens.refresh_token, "")

    def test_documented_200_mfa_challenge_is_completed(self):
        client = client_for(
            [
                Response({"challenge_name": "email_otp", "session": "challenge-session"}),
                Response({"access_token": "token", "expires_in": 3600}),
            ]
        )

        with patch("builtins.input", return_value="123456"):
            client._update_auth()

        self.assertEqual(client.tokens.access_token, "token")
        self.assertEqual(
            client._session.requests[1][1]["data"],
            {
                "grant_type": "email_otp",
                "username": "user@example.test",
                "session": "challenge-session",
                "email_otp": "123456",
            },
        )

    def test_oauth_error_payload_is_raised(self):
        client = client_for([Response({"error": "invalid_grant"})])

        with self.assertRaisesRegex(RuntimeError, "invalid_grant"):
            client._update_auth()

    def test_http_error_response_is_raised(self):
        client = client_for([Response({"detail": "invalid request"}, status_code=422)])

        with self.assertRaises(requests.HTTPError):
            client._update_auth()


if __name__ == "__main__":
    unittest.main()
