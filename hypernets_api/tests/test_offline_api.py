"""hypernets_api.subpackage_template.tests.test_module_template - describe class"""

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"
__all__ = []

import unittest
from hypernets_api.offline_api import OfflineHYPERNETSAPI
import os.path

example_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "examples")

class TestOfflineAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.api = OfflineHYPERNETSAPI(os.path.join(example_path,"example_archive"),"example_archive.db",
                                       data_path=os.path.join(example_path,"example_archive"))

    def test_query_filename(self):
        pass

    def test_query(self):
        query_dict = {"site": "GHNA",
                      "start_time": "2022-06-17T09:00:00",
                      "stop_time": "2022-06-17T11:00:00",
                      "level": "L_L2A", }
        assert (len(self.api.query(query_dict)) == 1)

        query_dict = {"geom": {
                        "latmin": 51.77632771952633,
                        "lonmin": -1.3399758460979756,
                        "latmax": 51.77808426115803,
                        "lonmax": -1.3370120963843524,
                        },
                      "level": "L_L2A", }
        print(self.api.query(query_dict))
        assert (len(self.api.query(query_dict)) == 1)


    def test_query_db_hypernets(self):
        pass


if __name__ == "__main__":
    unittest.main()
