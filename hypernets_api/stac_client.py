#!/usr/bin/env python3
"""
Example STAC API client for LANDHYPERNET Data Portal
Usage: python stac_client_example.py
"""

import requests
import json
from typing import Optional, List, Dict
from urllib.parse import urlencode

class LANDHYPERNETSTACClient:
    """Simple client for accessing LANDHYPERNET STAC API"""
    
    def __init__(self, base_url: str = "https://landhypernet.org", token: Optional[str] = None, verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.verify_ssl = verify_ssl
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def set_token(self, token: str):
        """Set or update API token"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def get_root_catalog(self) -> Dict:
        """Get root STAC catalog"""
        response = requests.get(f"{self.base_url}/stac/", verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()
    
    def get_collections(self) -> List[Dict]:
        """Get available collections"""
        response = requests.get(f"{self.base_url}/stac/collections", verify=self.verify_ssl)
        response.raise_for_status()
        data = response.json()
        return data.get("collections", [])
    
    def search(
        self,
        bbox: Optional[List[float]] = None,
        datetime: Optional[str] = None,
        site_id: Optional[str] = None,
        product_level: Optional[str] = None,
        limit: int = 100,
    ) -> Dict:
        """
        Search for STAC items
        
        Args:
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            datetime: Date range "YYYY-MM-DD/YYYY-MM-DD" or single date "YYYY-MM-DD"
            site_id: Filter by site ID
            product_level: Filter by product level (L1B_RAD, L1B_IRR, L2A, L1D_RAD, L1D_IRR, L2B)
            limit: Maximum number of results
        
        Returns:
            GeoJSON FeatureCollection with search results
        """
        if not self.token:
            raise ValueError("API token required for search. Use set_token()")
        
        params = {"limit": limit}
        
        if bbox:
            params["bbox"] = ",".join(str(x) for x in bbox)
        if datetime:
            params["datetime"] = datetime
        if site_id:
            params["site_id"] = site_id
        if product_level:
            params["product_level"] = product_level
        
        response = requests.get(
            f"{self.base_url}/stac/search",
            params=params,
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def get_item(self, sequence_name: str, collection_id: str) -> Dict:
        """Get a specific STAC item"""
        if not self.token:
            raise ValueError("API token required for item access. Use set_token()")
        
        response = requests.get(
            f"{self.base_url}/stac/collections/{collection_id}/items/{sequence_name}",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def search_by_site(self, site_id: str, limit: int = 100) -> Dict:
        """Search for all products at a specific site"""
        return self.search(site_id=site_id, limit=limit)
    
    def search_by_product_level(self, product_level: str, limit: int = 100) -> Dict:
        """Search for products of a specific level"""
        return self.search(product_level=product_level, limit=limit)
    
    def search_by_bbox(self, bbox: List[float], limit: int = 100) -> Dict:
        """Search for products within a bounding box"""
        return self.search(bbox=bbox, limit=limit)
    
    def search_by_date_range(self, start_date: str, end_date: str, limit: int = 100) -> Dict:
        """Search for products within a date range"""
        datetime_range = f"{start_date}/{end_date}"
        return self.search(datetime=datetime_range, limit=limit)
    
    def download_asset(self, asset_href: str, output_path: str) -> bool:
        """Download an asset to a local file.
        
        Args:
            asset_href: Relative or absolute URL to the asset (from STAC item)
            output_path: Local file path to save to
        
        Returns:
            True if successful, False otherwise
        """
        # Construct full URL if href is relative
        if asset_href.startswith('/'):
            url = f"{self.base_url}{asset_href}"
        else:
            url = asset_href
        
        try:
            response = requests.get(url, headers=self.headers, verify=self.verify_ssl, stream=True)
            response.raise_for_status()
            
            # Write file in chunks to handle large files
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✓ Downloaded to {output_path}")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False