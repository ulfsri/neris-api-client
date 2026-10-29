from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from pydantic import BaseModel, Field

from neris_api_client.config import Config, GrantType

from tests.helpers import FakeResponse, make_client


class AliasedPayload(BaseModel):
    display_name: str = Field(alias="displayName")


class ConfigTests(unittest.TestCase):
    def test_password_configuration_loads_from_environment(self) -> None:
        environment = {
            "NERIS_BASE_URL": "https://api.example.test/v1",
            "NERIS_GRANT_TYPE": "password",
            "NERIS_USERNAME": "user@example.test",
            "NERIS_PASSWORD": "secret",
            "NERIS_DEBUG": "true",
            "NERIS_VALIDATE": "true",
        }

        with patch.dict(os.environ, environment, clear=True):
            config = Config()

        self.assertEqual(config.base_url, environment["NERIS_BASE_URL"])
        self.assertEqual(config.grant_type, GrantType.PASSWORD)
        self.assertEqual(config.username, environment["NERIS_USERNAME"])
        self.assertEqual(config.password, environment["NERIS_PASSWORD"])
        self.assertTrue(config.debug)
        self.assertTrue(config.validate)

    def test_explicit_boolean_options_override_environment(self) -> None:
        environment = {
            "NERIS_DEBUG": "true",
            "NERIS_VALIDATE": "true",
        }

        with patch.dict(os.environ, environment, clear=True):
            config = Config(debug=False, validate=False)

        self.assertFalse(config.debug)
        self.assertFalse(config.validate)


class AuthenticationTests(unittest.TestCase):
    def test_unexpired_access_token_does_not_make_a_token_request(self) -> None:
        client, session = make_client()

        client._update_auth()

        self.assertEqual(session.requests, [])

    def test_password_grant_stores_successful_token_response(self) -> None:
        client, session = make_client(
            [
                FakeResponse(
                    {
                        "access_token": "new-access-token",
                        "refresh_token": "new-refresh-token",
                        "expires_in": 3600,
                    }
                )
            ],
            authenticated=False,
        )

        client._update_auth()

        self.assertEqual(client.tokens.access_token, "new-access-token")
        self.assertEqual(client.tokens.refresh_token, "new-refresh-token")
        self.assertEqual(session.requests[0][0:2], ("post", "https://api.example.test/v1/token"))
        self.assertEqual(
            session.requests[0][2]["data"],
            {
                "grant_type": GrantType.PASSWORD,
                "username": "user@example.test",
                "password": "secret",
            },
        )


class TransportTests(unittest.TestCase):
    def test_json_response_is_decoded_and_authorization_is_added(self) -> None:
        client, session = make_client([FakeResponse({"status": "ok"})])

        result = client._call("get", "/health")

        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(session.headers["Authorization"], "Bearer access-token")
        self.assertEqual(
            session.requests,
            [
                (
                    "get",
                    "https://api.example.test/v1/health",
                    {"json": None, "params": None},
                )
            ],
        )

    def test_non_json_response_returns_text(self) -> None:
        client, _ = make_client([FakeResponse(text="healthy")])

        result = client._call("get", "/health")

        self.assertEqual(result, "healthy")

    def test_validated_payload_uses_api_aliases(self) -> None:
        client, session = make_client([FakeResponse({"created": True})], validate=True)

        client._call(
            "post",
            "/example",
            data={"displayName": "Station 1"},
            model=AliasedPayload,
        )

        self.assertEqual(session.requests[0][2]["json"], {"displayName": "Station 1"})


if __name__ == "__main__":
    unittest.main()
