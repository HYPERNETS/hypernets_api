import os.path
import sqlite3
import socket
import numpy as np
import glob, os
from pathlib import Path
from typing import Optional, List, Dict
import datetime

from hypernets_api.base import BaseAPI
from hypernets_api.stac_client import LANDHYPERNETSTACClient

class HYPERNETSAPI(BaseAPI):
    def __init__(self,api_token:str, base_url="https://landhypernet.org.uk", verify_ssl=False, limit=100):
        self.client = LANDHYPERNETSTACClient(token=api_token, base_url=base_url, verify_ssl=verify_ssl)
        self.limit = limit

    def query_sequence(self,sequence,product_level):
        return self.client.get_item(sequence_name=sequence,product_level=product_level)

    def query(self, query_dict):
        if "site" in query_dict:
            site=query_dict["site"]
            geom=None
        elif "site_id" in query_dict:
            site=query_dict["site_id"]
            geom=None
        elif "geom" in query_dict:
            site=None
            geom=query_dict["geom"]
        else:
            site=None
            geom=None

        if "product_level" in query_dict:
            level=query_dict["product_level"]
        elif "collection" in query_dict:
            level=query_dict["collection"]
        elif "level" in query_dict:
            level=query_dict["level"]            
        else:
            level=None

        if "start_time" in query_dict:
            start_time=query_dict["start_time"]
        else:
            start_time="2021-11-01"

        if "stop_time" in query_dict:
            stop_time=query_dict["stop_time"]
        else:
            stop_time=datetime.datetime.now().isoformat()

        if "datetime" in query_dict:
            datetime = query_dict["datetime"]
        else:
            datetime = f"{start_time}/{stop_time}"

        return self.client.search(
                bbox=geom,
                datetime= datetime,
                site_id=site,
                product_level=level,
                limit=self.limit
            )
    
    def download_results(self, results: dict, output_path: str) -> List[str]: 
        for feature in results["features"]:
            props = feature["properties"]
            asset = feature["assets"]["data"]

            sequence = props["sequence_name"]
            dt = props["datetime"]
            href = asset["href"]

            print(sequence, dt, href)
            self.client.download_asset(href,output_path)


