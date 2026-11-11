from datetime import datetime
from types import SimpleNamespace
import unittest

from neris_api_client.client import _NerisApiClient


class Response:
    def raise_for_status(self):
        pass

    def json(self):
        return {}


class Session:
    def __init__(self):
        self.headers = {}
        self.kwargs = None

    def post(self, *args, **kwargs):
        self.kwargs = kwargs
        return Response()


class PayloadSerializationTests(unittest.TestCase):
    def test_json_string_payload_is_sent_as_a_json_object_without_validation(self):
        client = object.__new__(_NerisApiClient)
        client.config = SimpleNamespace(base_url="https://api.example.test", debug=False, validate=False)
        client.tokens = SimpleNamespace(access_token="token", expires_at=datetime.max)
        client._session = Session()
        client._update_auth = lambda: None

        client._call("post", "/entity", data='{"name": "Example Fire Department"}')

        self.assertEqual(client._session.kwargs["json"], {"name": "Example Fire Department"})


if __name__ == "__main__":
    unittest.main()
