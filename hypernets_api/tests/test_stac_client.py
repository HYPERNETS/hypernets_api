import os
import tempfile
import unittest
from unittest.mock import patch
from hypernets_api.stac_client import LANDHYPERNETSTACClient


class DummyResponse:
    def __init__(self, json_data=None, status_code=200, content=b""):
        self._json_data = json_data or {}
        self.status_code = status_code
        self._content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data

    def iter_content(self, chunk_size=8192):
        yield self._content


class TestLANDHYPERNETSTACClient(unittest.TestCase):
    def test_set_token_adds_authorization_header(self):
        client = LANDHYPERNETSTACClient(base_url="https://example.com")
        client.set_token("abcd")
        self.assertEqual(client.headers["Authorization"], "Bearer abcd")

    @patch("hypernets_api.stac_client.requests.get")
    def test_get_root_catalog_returns_json(self, mock_get):
        mock_get.return_value = DummyResponse(json_data={"root": True})
        client = LANDHYPERNETSTACClient(base_url="https://example.com")
        result = client.get_root_catalog()
        self.assertEqual(result, {"root": True})
        mock_get.assert_called_once_with("https://example.com/stac/", verify=False)

    @patch("hypernets_api.stac_client.requests.get")
    def test_get_collections_returns_collection_list(self, mock_get):
        mock_get.return_value = DummyResponse(json_data={"collections": [{"id": "c1"}]})
        client = LANDHYPERNETSTACClient(base_url="https://example.com")
        result = client.get_collections()
        self.assertEqual(result, [{"id": "c1"}])

    @patch("hypernets_api.stac_client.requests.get")
    def test_search_builds_expected_query_params(self, mock_get):
        def fake_get(url, params=None, headers=None, verify=None):
            self.assertEqual(url, "https://example.com/stac/search")
            self.assertEqual(params["limit"], "1")
            self.assertEqual(params["bbox"], "1,2,3,4")
            self.assertEqual(params["datetime"], "2022-01-01/2022-01-02")
            self.assertEqual(params["site_id"], "GHNA")
            self.assertEqual(params["product_level"], "L2A")
            self.assertEqual(headers["Authorization"], "Bearer token")
            return DummyResponse(json_data={"results": []})

        mock_get.side_effect = fake_get
        client = LANDHYPERNETSTACClient(base_url="https://example.com", token="token")
        result = client.search(
            bbox=[1, 2, 3, 4],
            datetime="2022-01-01/2022-01-02",
            site_id="GHNA",
            product_level="L2A",
            limit=1,
        )
        self.assertEqual(result, {"results": []})

    def test_search_requires_authentication(self):
        client = LANDHYPERNETSTACClient(base_url="https://example.com")
        with self.assertRaises(RuntimeError):
            client.search(site_id="GHNA")

    @patch("hypernets_api.stac_client.requests.get")
    def test_download_asset_writes_file(self, mock_get):
        mock_get.return_value = DummyResponse(content=b"hello")
        client = LANDHYPERNETSTACClient(base_url="https://example.com", token="token")
        with tempfile.TemporaryDirectory() as tempdir:
            client.download_asset("https://example.com/file.nc", tempdir)
            output_path = os.path.join(tempdir, "file.nc")
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "rb") as f:
                self.assertEqual(f.read(), b"hello")

    @patch("hypernets_api.stac_client.requests.get")
    def test_get_item_calls_collection_endpoint(self, mock_get):
        mock_get.return_value = DummyResponse(json_data={"item": "ok"})
        client = LANDHYPERNETSTACClient(base_url="https://example.com", token="token")
        result = client.get_item("sequence_1", "L2A")
        self.assertEqual(result, {"item": "ok"})
        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
