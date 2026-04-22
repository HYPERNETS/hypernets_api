from hypernets_api.stac_client import LANDHYPERNETSTACClient
import requests
from typing import Optional, List, Dict 

def main():
    """Example usage"""
    
    # Initialize client (use localhost for local development, production URL for remote)
    base_url = input("Enter base URL (default: http://landhypernet.org.uk): ").strip()
    if not base_url:
        base_url = "http://landhypernet.org.uk"
    
    client = LANDHYPERNETSTACClient(base_url=base_url)
    
    print("=" * 60)
    print("LANDHYPERNET STAC API Example Client")
    print(f"Connecting to: {base_url}")
    print("=" * 60)
    
    # Get root catalog (no auth required)
    print("\n1. Getting root catalog...")
    catalog = client.get_root_catalog()
    print(f"   Catalog ID: {catalog['id']}")
    print(f"   Description: {catalog['description']}")
    
    # Get collections (no auth required)
    print("\n2. Getting collections...")
    collections = client.get_collections()
    print(f"   Available collections: {len(collections)}")
    for coll in collections:
        print(f"     - {coll['id']}: {coll['description']}")
    
    # For searching, you need an API token
    print("\n3. To search for data, you need an API token:")
    print(f"   a. Log in to {base_url}")
    print(f"   b. Go to {base_url}/api/token/generate and generate your token")
    print(f"   c. Use the token here:")
    
    # Example with mock token (would fail with invalid token)
    token = input("\n   Enter your API token (or press Enter to skip): ").strip()
    
    if token:
        try:
            client.set_token(token)
            
            print("\n4. Searching for L2B products at GHNA site (limit 5)...")
            results = client.search(
                site_id="GHNA",
                product_level="L2B",
                limit=5
            )
            
            features = results.get("features", [])
            print(f"   Found {len(features)} products")
            
            for i, feature in enumerate(features[:3], 1):
                props = feature["properties"]
                print(f"\n   Product {i}:")
                print(f"     Sequence: {props['sequence_name']}")
                print(f"     Date: {props['datetime']}")
                print(f"     Location: ({props['latitude']:.2f}, {props['longitude']:.2f})")
                print(f"     Data: {feature['assets']['data']['href']}")
            
            print("\n5. Other search examples:")
            print("   - Search by bounding box:")
            print("     results = client.search_by_bbox([8, 33, 12, 37], limit=10)")
            print("   - Search by date range:")
            print("     results = client.search_by_date_range('2024-01-01', '2024-12-31', limit=50)")
            print("   - Search by site:")
            print("     results = client.search_by_site('CRAU', limit=10)")
            
        except requests.exceptions.HTTPError as e:
            print(f"   Error: {e.response.status_code} - {e.response.json()}")
    else:
        print("   Skipping search example (token required)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
