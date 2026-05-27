"""Tests for the offline HYPERNETS API implementation."""

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from hypernets_api.offline_api import OfflineHYPERNETSAPI

example_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "examples")


class TestOfflineAPIWithExampleData(unittest.TestCase):
    def setUp(self) -> None:
        self.api = OfflineHYPERNETSAPI(
            os.path.join(example_path, "example_archive"),
            "example_archive.db",
            data_path=os.path.join(example_path, "example_archive"),
        )

    def test_query_returns_expected_row_by_site(self):
        query_dict = {
            "site": "GHNA",
            "start_time": "2022-06-17T09:00:00",
            "stop_time": "2022-06-17T11:00:00",
            "product_level": "L_L2A",
        }
        result = self.api.query(query_dict)
        self.assertEqual(len(result), 1)

    def test_query_returns_expected_row_by_geom(self):
        query_dict = {
            "geom": {
                "latmin": 51.77632771952633,
                "lonmin": -1.3399758460979756,
                "latmax": 51.77808426115803,
                "lonmax": -1.3370120963843524,
            },
            "product_level": "L_L2A",
        }
        result = self.api.query(query_dict)
        self.assertEqual(len(result), 1)


class TestOfflineHYPERNETSAPIUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.archive_path = Path(self.tempdir.name) / "archive"
        self.archive_path.mkdir(parents=True)
        self.db_path = self.archive_path / "test_archive.db"
        self.data_path = Path(self.tempdir.name) / "data"
        self.data_path.mkdir(parents=True)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE products (
                sequence_name TEXT,
                site_id TEXT,
                system_id TEXT,
                datetime_SEQ TEXT,
                datetime_start TEXT,
                datetime_end TEXT,
                latitude REAL,
                longitude REAL,
                product_name TEXT,
                rel_product_dir TEXT,
                product_path TEXT
            )
            """
        )
        cursor.execute(
            "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                "sequence_1",
                "GHNA",
                "SYS1",
                "2022-01-01 00:00:00",
                "2022-01-01 00:00:00",
                "2022-01-01 00:10:00",
                51.0,
                -1.0,
                "sequence_1",
                "rel\\path",
                "C:/ignore/path/sequence_1.nc",
            ],
        )
        connection.commit()
        connection.close()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_init_raises_for_missing_archive_path(self):
        with self.assertRaises(ValueError):
            OfflineHYPERNETSAPI("/does/not/exist", archive_db="test.db")

    def test_query_filename_finds_single_file(self):
        nested_dir = self.archive_path / "a" / "b" / "c" / "d" / "e"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / "target.nc"
        file_path.write_text("test")

        api = OfflineHYPERNETSAPI(str(self.archive_path), archive_db="test_archive.db")
        result = api.query_filename("target.nc")
        self.assertEqual(Path(result), file_path)

    def test_query_filename_raises_for_missing_file(self):
        api = OfflineHYPERNETSAPI(str(self.archive_path), archive_db="test_archive.db")
        with self.assertRaises(ValueError):
            api.query_filename("missing.nc")

    def test_query_filename_raises_for_multiple_files(self):
        for i in range(2):
            nested_dir = self.archive_path / f"dir{i}" / "sub" / "sub2" / "sub3" / "sub4"
            nested_dir.mkdir(parents=True)
            (nested_dir / "duplicate.nc").write_text("x")

        api = OfflineHYPERNETSAPI(str(self.archive_path), archive_db="test_archive.db")
        with self.assertRaises(ValueError):
            api.query_filename("duplicate.nc")

    def test_query_db_hypernets_returns_normalized_result(self):
        api = OfflineHYPERNETSAPI(
            str(self.archive_path),
            archive_db="test_archive.db",
            data_path=str(self.data_path),
        )
        query = (
            "SELECT sequence_name,site_id,system_id,datetime_SEQ,datetime_start,datetime_end,latitude,longitude,"
            "product_name,rel_product_dir,product_path FROM products"
        )
        results = api.query_db_hypernets(query)
        self.assertEqual(len(results), 1)
        row = results[0]
        self.assertEqual(row["sequence_name"], "sequence_1")
        self.assertEqual(row["site_id"], "GHNA")
        self.assertTrue(row["product_path"].endswith(os.path.join(str(self.data_path), "rel", "path", "sequence_1.nc")))
        self.assertEqual(row["rel_product_dir"], os.path.relpath("rel" + os.sep + "path"))

    def test_query_raises_for_invalid_product_level(self):
        api = OfflineHYPERNETSAPI(str(self.archive_path), archive_db="test_archive.db")
        with self.assertRaises(ValueError):
            api.query({"product_level": "INVALID_LEVEL"})


if __name__ == "__main__":
    unittest.main()
