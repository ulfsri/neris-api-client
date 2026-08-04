from datetime import datetime
from types import SimpleNamespace
import unittest

from neris_api_client.client import _NerisApiClient
from neris_api_client.config import GrantType, TokenSet


class Response:
    status_code = 200
    headers = {}
    text = ""

    def json(self):
        return {"access_token": "token", "expires_in": 3600}


class Session:
    def post(self, *args, **kwargs):
        return Response()


class OptionalRefreshTokenTests(unittest.TestCase):
    def test_successful_token_response_without_refresh_token_is_accepted(self):
        client = object.__new__(_NerisApiClient)
        client.config = SimpleNamespace(
            base_url="https://api.example.test",
            debug=False,
            grant_type=GrantType.CLIENT_CREDENTIALS,
        )
        client.client_creds = "credentials"
        client.tokens = TokenSet(access_token="", refresh_token="", expires_at=datetime.min)
        client._session = Session()

        client._update_auth()

        self.assertEqual(client.tokens.access_token, "token")
        self.assertEqual(client.tokens.refresh_token, "")


if __name__ == "__main__":
    unittest.main()
