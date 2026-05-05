
#!/usr/bin/env python3
"""
Example STAC API client for LANDHYPERNET Data Portal
Usage: python stac_client_example.py
"""

import os.path
import requests
from typing import Optional, List, Dict


class LANDHYPERNETSTACClient:
    """Simple client for accessing the LANDHYPERNET STAC API"""

    def __init__(
        self,
        base_url: str = "https://landhypernet.org.uk",
        token: Optional[str] = None,
        verify_ssl: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.headers: Dict[str, str] = {}

        if token:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        """Set or update API token"""
        self.headers["Authorization"] = f"Bearer {token}"

    # ------------------------------------------------------------------
    # Public endpoints (no authentication required)
    # ------------------------------------------------------------------

    def get_root_catalog(self) -> Dict:
        """Get the root STAC catalog"""
        r = requests.get(
            f"{self.base_url}/stac/",
            verify=self.verify_ssl,
        )
        r.raise_for_status()
        return r.json()

    def get_collections(self) -> List[Dict]:
        """Get available STAC collections"""
        r = requests.get(
            f"{self.base_url}/stac/collections",
            verify=self.verify_ssl,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("collections", [])

    # ------------------------------------------------------------------
    # Authenticated endpoints
    # ------------------------------------------------------------------

    def search(
        self,
        bbox: Optional[List[float]] = None,
        datetime: Optional[str] = None,
        site_id: Optional[str] = None,
        product_level: Optional[str] = None,
        limit: int = 50,
    ) -> Dict:
        """
        Search for STAC items.

        Args:
            bbox: [min_lon, min_lat, max_lon, max_lat]
            datetime: "YYYY-MM-DD/YYYY-MM-DD" or "YYYY-MM-DD"
            site_id: Site identifier (e.g. GHNA)
            product_level: L1B_RAD, L1B_IRR, L2A, L1D_RAD, L1D_IRR, L2B
            limit: Maximum number of results

        Returns:
            STAC FeatureCollection
        """
        if "Authorization" not in self.headers:
            raise RuntimeError("API token required for search")

        params: Dict[str, str] = {"limit": str(limit)}

        if bbox:
            params["bbox"] = ",".join(str(v) for v in bbox)
        if datetime:
            params["datetime"] = datetime
        if site_id:
            params["site_id"] = site_id
        if product_level:
            params["product_level"] = product_level

        r = requests.get(
            f"{self.base_url}/stac/search",
            params=params,
            headers=self.headers,
            verify=self.verify_ssl,
        )
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def search_by_site(self, site_id: str, limit: int = 100) -> Dict:
        """Search for all products at a specific site"""
        return self.search(site_id=site_id, limit=limit)

    def search_by_product_level(self, product_level: str, limit: int = 100) -> Dict:
        """Search for products of a specific level"""
        return self.search(product_level=product_level, limit=limit)

    def search_by_bbox(self, bbox: List[float], limit: int = 100) -> Dict:
        """Search for products within a bounding box"""
        return self.search(bbox=bbox, limit=limit)

    def search_by_date_range(
        self, start_date: str, end_date: str, limit: int = 100
    ) -> Dict:
        return self.search(datetime=f"{start_date}/{end_date}", limit=limit)

    # ------------------------------------------------------------------
    # Asset download
    # ------------------------------------------------------------------

    def download_asset(self, asset_href: str, output_path: str) -> None:
        """
        Download a STAC asset.

        asset_href may be absolute or relative.
        """
        if asset_href.startswith("/"):
            url = f"{self.base_url}{asset_href}"
        else:
            url = asset_href

        r = requests.get(
            url,
            headers=self.headers,
            verify=self.verify_ssl,
            stream=True,
        )
        r.raise_for_status()
        output_file_path = os.path.join(output_path, asset_href.split("/")[-1])

        with open(output_file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✓ Downloaded {output_file_path}")


    def get_item(self, sequence_name: str, product_level: str) -> Dict:
        """
        Retrieve a single STAC Item by sequence name and product level.

        Args:
            sequence_name: LANDHYPERNET sequence identifier
            product_level: L1B_RAD, L1B_IRR, L2A_REF, L1D_RAD, L1D_IRR, or L2B_REF (L2A and L2B are not canonical but also accepted)

        Returns:
            STAC Item (Feature)

        Raises:
            RuntimeError if item is not found or ambiguous
        """
        collection_map =  {
                "L1B_RAD": "L1B_RAD",
                "L1B_IRR": "L1B_IRR",
                "L2A": "L2A_REF",
                "L1D_RAD": "L1D_RAD",
                "L1D_IRR": "L1D_IRR",
                "L2B": "L2B_REF",
                "L2A_REF": "L2A_REF",
                "L2B_REF": "L2B_REF",
            }
        
        collection_id = collection_map[product_level]

        r = requests.get(
            f"{self.base_url}/stac/collections/{collection_id}/items/{sequence_name}",
            headers=self.headers,
            verify=self.verify_ssl,
        )
        r.raise_for_status()
        return r.json()
