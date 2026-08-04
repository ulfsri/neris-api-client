from datetime import datetime
from types import SimpleNamespace
import unittest

import requests

from neris_api_client.client import _NerisApiClient


class ErrorResponse:
    status_code = 400
    headers = {}
    text = '{"detail": "invalid request"}'

    def raise_for_status(self):
        error = requests.HTTPError("400 Client Error")
        error.response = self
        raise error

    def json(self):
        return {"detail": "invalid request"}


class Session:
    def __init__(self):
        self.headers = {}

    def get(self, *args, **kwargs):
        return ErrorResponse()


class HttpErrorTests(unittest.TestCase):
    def test_api_http_errors_are_raised_with_response_details(self):
        client = object.__new__(_NerisApiClient)
        client.config = SimpleNamespace(base_url="https://api.example.test", debug=False, validate=False)
        client.tokens = SimpleNamespace(access_token="token", expires_at=datetime.max)
        client._session = Session()
        client._update_auth = lambda: None

        with self.assertRaises(requests.HTTPError) as context:
            client._call("get", "/entity/FD24000001")

        self.assertEqual(context.exception.args[-1], {"detail": "invalid request"})


if __name__ == "__main__":
    unittest.main()
