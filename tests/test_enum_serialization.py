from datetime import datetime
from types import SimpleNamespace
import unittest

from neris_api_client.client import NerisApiClient, _NerisApiClient
from neris_api_client.models import StatesTerrs, TypeIncidentStatusValue


class Response:
    def raise_for_status(self):
        pass

    def json(self):
        return {}


class Session:
    def __init__(self):
        self.headers = {}
        self.kwargs = None

    def get(self, *args, **kwargs):
        self.kwargs = kwargs
        return Response()


class EnumSerializationTests(unittest.TestCase):
    def test_query_enum_uses_its_api_value(self):
        client = object.__new__(_NerisApiClient)
        client.config = SimpleNamespace(base_url="https://api.example.test", debug=False, validate=False)
        client.tokens = SimpleNamespace(access_token="token", expires_at=datetime.max)
        client._session = Session()
        client._update_auth = lambda: None

        client._call("get", "/entity", params={"state": StatesTerrs.AL})

        self.assertEqual(client._session.kwargs["params"], {"state": "AL"})

    def test_incident_status_uses_its_api_value(self):
        client = object.__new__(NerisApiClient)
        calls = []
        client._call = lambda *args, **kwargs: calls.append((args, kwargs))

        NerisApiClient.update_incident_status(
            client, "FD24000001", "IN24000001", TypeIncidentStatusValue.APPROVED
        )

        self.assertEqual(calls[0][1]["data"], {"status": "APPROVED"})


if __name__ == "__main__":
    unittest.main()
