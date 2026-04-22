import os.path
import sqlite3
import socket
import numpy as np
import glob, os
from pathlib import Path

from hypernets_api.base import BaseAPI
from hypernets_api.stac_client import LANDHYPERNETSTACClient

class OnlineHYPERNETSAPI(BaseAPI):
    def __init__(self,api_token:str, base_url="https://landhypernet.org.uk", verify_ssl=True, limit=100):
        self.client = LANDHYPERNETSTACClient(token=api_token, base_url=base_url, verify_ssl=verify_ssl)
        self.limit = limit

    def query_filename(self,filename):
        pass

    def query(self, query_dict):
        if "site" in query_dict:
            site=query_dict["site"]
            geom=None
        elif "geom" in query_dict:
            site=None
            geom=query_dict["geom"]
        else:
            site=None
            geom=None

        if "collection" in query_dict:
            level=query_dict["collection"][-3::]
        elif "level" in query_dict:
            level=query_dict["level"]
        else:
            level=None

        if "start_time" in query_dict:
            start_time=query_dict["start_time"]
        else:
            start_time=None

        if "stop_time" in query_dict:
            stop_time=query_dict["stop_time"]
        else:
            stop_time=None

        if "only_passed_qc" in query_dict:
            only_passed_qc=query_dict["only_passed_qc"]
        else:
            only_passed_qc=False

        return self.client.search(
                bbox=geom,
                datetime=f"{start_time}/{stop_time}" if start_time and stop_time else None,
                site_id=site,
                product_level=level,
                limit=self.limit
            )
