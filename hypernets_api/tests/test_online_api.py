import unittest
from unittest.mock import MagicMock, patch
from hypernets_api.online_api import HYPERNETSAPI


class TestHYPERNETSAPI(unittest.TestCase):
    @patch("hypernets_api.online_api.LANDHYPERNETSTACClient")
    def test_query_calls_search_with_expected_parameters(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.search.return_value = {"features": []}
        mock_client_cls.return_value = mock_client

        api = HYPERNETSAPI(api_token="fake-token", base_url="https://example.com", verify_ssl=True, limit=5)
        result = api.query(
            {
                "site": "GHNA",
                "product_level": "L2A",
                "start_time": "2022-01-01",
                "stop_time": "2022-01-02",
            }
        )

        self.assertEqual(result, {"features": []})
        mock_client.search.assert_called_once_with(
            bbox=None,
            datetime="2022-01-01/2022-01-02",
            site_id="GHNA",
            product_level="L2A",
            limit=5,
        )

    @patch("hypernets_api.online_api.LANDHYPERNETSTACClient")
    def test_query_sequence_calls_get_item(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.get_item.return_value = {"item": "ok"}
        mock_client_cls.return_value = mock_client

        api = HYPERNETSAPI(api_token="token")
        result = api.query_sequence("sequence_1", "L2A")

        self.assertEqual(result, {"item": "ok"})
        mock_client.get_item.assert_called_once_with(sequence_name="sequence_1", product_level="L2A")

    @patch("hypernets_api.online_api.LANDHYPERNETSTACClient")
    def test_download_results_calls_download_asset_for_each_feature(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        api = HYPERNETSAPI(api_token="token")
        results = {
            "features": [
                {
                    "properties": {"sequence_name": "sequence_1", "datetime": "2022-01-01T00:00:00"},
                    "assets": {"data": {"href": "https://example.com/file.nc"}},
                }
            ]
        }

        api.download_results(results, output_path="/tmp/output")

        mock_client.download_asset.assert_called_once_with("https://example.com/file.nc", "/tmp/output")


if __name__ == "__main__":
    unittest.main()
