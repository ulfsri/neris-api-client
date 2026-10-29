import unittest

from neris_api_client.client import NerisApiClient
from neris_api_client.config import Config, GrantType


def client_config(client_id: str) -> Config:
    return Config(
        base_url="https://api.example.test/v1",
        grant_type=GrantType.CLIENT_CREDENTIALS,
        client_id=client_id,
        client_secret="secret",
    )


class ClientStateTests(unittest.TestCase):
    def test_clients_do_not_share_sessions_or_tokens(self):
        first = NerisApiClient(client_config("first"))
        second = NerisApiClient(client_config("second"))

        first.tokens.access_token = "first-token"
        first._session.headers["Authorization"] = "Bearer first-token"

        self.assertIsNot(first._session, second._session)
        self.assertEqual(second.tokens.access_token, "")
        self.assertNotIn("Authorization", second._session.headers)


if __name__ == "__main__":
    unittest.main()
