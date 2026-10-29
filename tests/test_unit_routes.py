import unittest

from neris_api_client.client import NerisApiClient


class UnitRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = object.__new__(NerisApiClient)
        self.calls = []
        self.client._call = lambda *args, **kwargs: self.calls.append((args, kwargs))

    def test_create_unit_uses_unit_collection_route(self):
        NerisApiClient.create_unit(self.client, "FD24000001", "ST24000001", {"name": "E1"})

        self.assertEqual(
            self.calls[0][0],
            ("post", "/entity/FD24000001/station/ST24000001/unit"),
        )

    def test_patch_unit_uses_entity_id_parameter(self):
        NerisApiClient.patch_unit(
            self.client,
            "FD24000001",
            "ST24000001",
            "UN24000001",
            {"name": "E2"},
        )

        self.assertEqual(
            self.calls[0][0],
            ("patch", "/entity/FD24000001/station/ST24000001/unit/UN24000001"),
        )


if __name__ == "__main__":
    unittest.main()
