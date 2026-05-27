import os.path
import sqlite3
import socket
import numpy as np
import glob, os
import re

from hypernets_api.base import BaseAPI


class OfflineHYPERNETSAPI(BaseAPI):
    def __init__(self,archive_path,archive_db="archive.db",data_path=None):
        if archive_path is None:
            if socket.gethostname() == "eoserver.npl.co.uk":
                archive_path = os.path.abspath(r"/home/data/insitu/hypernets/archive")
            elif socket.gethostname() == "lyon.npl.co.uk":
                archive_path = r"/mnt/t/data/insitu/hypernets/archive"
            else:
                archive_path = os.path.abspath(r"\\eoserver\home\data\insitu\hypernets\archive")

        if archive_db in archive_path:
            archive_path=archive_path.replace(archive_db,"")

        if not os.path.exists(archive_path):
            raise ValueError("The archive path does not exists: ",archive_path)

        self.archive_path=archive_path
        self.archive_db_path=os.path.join(archive_path, archive_db)

        if data_path is not None:
            self.data_path = data_path
            self.overwrite_product_path = True
        else:
            self.overwrite_product_path = False

    def query_filename(self,filename):
        files = glob.glob(self.archive_path+"/*/*/*/*/*/"+filename)
        if len(files)==1:
            return files[0]
        elif len(files)>1:
            raise ValueError("Multiple files were found with this filename (%s), please check your file directory (%s)."%(filename,self.archive_path))
        else:
            raise ValueError("No files were found with this filename (%s), please check your file directory (%s)."%(filename,self.archive_path))

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
            collection=query_dict["collection"]
            level_map = {
                "L1B_RAD": "L_L1B_RAD",
                "L1B_IRR": "L_L1B_IRR",
                "L2A": "L_L2A",
                "L1D_RAD": "L_L1D_RAD",
                "L1D_IRR": "L_L1D_IRR",
                "L2B": "L_L2B",
                "L2A_REF": "L_L2A",
                "L2B_REF": "L_L2B"
            }
            level = level_map.get(collection, None)
        elif "product_level" in query_dict:
            level=query_dict["product_level"]
            level_map = {
                "L1B_RAD": "L_L1B_RAD",
                "L1B_IRR": "L_L1B_IRR",
                "L2A": "L_L2A",
                "L1D_RAD": "L_L1D_RAD",
                "L1D_IRR": "L_L1D_IRR",
                "L2B": "L_L2B",
                "L2A_REF": "L_L2A",
                "L2B_REF": "L_L2B"
            }
            if level not in level_map and level not in level_map.values():
                raise ValueError("product_level should be one of: L1B_RAD, L1B_IRR, L2A, L1D_RAD, L1D_IRR, L2B, L2A_REF or L2B_REF")
            level = level_map.get(level, level)
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

        query = self.make_query_hypernets(
            site_id=site, geom=geom, start_time=start_time, stop_time=stop_time, product_level=level, only_passed_qc=only_passed_qc
        )
        print(query)
        return self.query_db_hypernets(query)

    def query_db_hypernets(
        self, query,
    ):
        engine = sqlite3.connect(self.archive_db_path)
        cursor = engine.cursor()

        try:
            cursor.execute(query)
            data = cursor.fetchall()
            if len(data) == 0:
                raise ValueError(
                    "no data found between the specified dates in the hypernets database"
                )
            result_dicts = []
            for i in range(len(data)):
                data[i] = list(data[i])
                
                # Normalize any Windows-style separators from DB to the current OS
                rel_prod_norm = data[i][9].replace('\\', os.sep).replace('/', os.sep)
                prod_path_norm = data[i][10].replace('\\', os.sep).replace('/', os.sep)


                if self.overwrite_product_path:
                    filename = data[i][-3] + ".nc"
                    prod_path_norm = os.path.abspath(os.path.join(self.data_path, rel_prod_norm, filename))
                

                data_dict = {
                    "sequence_name": data[i][0],
                    "site_id": data[i][1],
                    "system_id": data[i][2],
                    "datetime_SEQ": data[i][3],
                    "datetime_start": data[i][4],
                    "datetime_end": data[i][5],
                    "latitude": data[i][6],
                    "longitude": data[i][7],
                    "product_name": data[i][8],
                    "rel_product_dir": os.path.relpath(rel_prod_norm) if rel_prod_norm else "",
                    "product_path": os.path.abspath(prod_path_norm) if prod_path_norm else "",
                }
                result_dicts.append(data_dict)
            return result_dicts
        finally:
            engine.close()


