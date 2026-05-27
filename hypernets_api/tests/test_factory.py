import unittest
from hypernets_api.factory import APIFactory
from hypernets_api.offline_api import OfflineHYPERNETSAPI
from hypernets_api.online_api import HYPERNETSAPI


class TestAPIFactory(unittest.TestCase):
    def test_get_api_offline_returns_offline_class(self):
        factory = APIFactory()
        self.assertIs(factory.get_api("offline"), OfflineHYPERNETSAPI)

    def test_get_api_online_returns_online_class(self):
        factory = APIFactory()
        self.assertIs(factory.get_api("online"), HYPERNETSAPI)

    def test_get_api_invalid_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            APIFactory().get_api("missing")


if __name__ == "__main__":
    unittest.main()
