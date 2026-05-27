import datetime
import unittest
from shapely.geometry import Point, Polygon
from hypernets_api.base import BaseAPI


class TestBaseAPI(unittest.TestCase):
    def test_convert_datetime_from_datetime(self):
        value = datetime.datetime(2022, 1, 2, 3, 4, 5)
        self.assertEqual(BaseAPI.convert_datetime(value), "2022-01-02 03:04:05")

    def test_convert_datetime_from_date(self):
        value = datetime.date(2022, 1, 2)
        self.assertEqual(BaseAPI.convert_datetime(value), "2022-01-02")

    def test_convert_datetime_from_string_with_z(self):
        self.assertEqual(BaseAPI.convert_datetime("2022-01-02T03:04:05Z"), "2022-01-02 03:04:05")

    def test_convert_datetime_invalid_string_raises(self):
        with self.assertRaises(ValueError):
            BaseAPI.convert_datetime("not-a-datetime")

    def test_convert_geom_from_list(self):
        value = [10.0, 20.0, 11.0, 21.0]
        expected = {"latmin": 10.0, "lonmin": 20.0, "latmax": 11.0, "lonmax": 21.0}
        self.assertEqual(BaseAPI.convert_geom(value), expected)

    def test_convert_geom_from_tuple(self):
        value = (10.0, 20.0, 11.0, 21.0)
        expected = {"latmin": 10.0, "lonmin": 20.0, "latmax": 11.0, "lonmax": 21.0}
        self.assertEqual(BaseAPI.convert_geom(value), expected)

    def test_convert_geom_from_dict(self):
        value = {"latmin": 10.0, "lonmin": 20.0, "latmax": 11.0, "lonmax": 21.0}
        self.assertEqual(BaseAPI.convert_geom(value), value)

    def test_convert_geom_from_point(self):
        value = Point(20.0, 10.0)
        expected = {"latmin": 10.0, "lonmin": 20.0, "latmax": 10.0, "lonmax": 20.0}
        self.assertEqual(BaseAPI.convert_geom(value), expected)

    def test_convert_geom_from_polygon(self):
        value = Polygon([(1.0, 2.0), (1.0, 3.0), (2.0, 3.0), (2.0, 2.0)])
        expected = {"latmin": 2.0, "lonmin": 1.0, "latmax": 3.0, "lonmax": 2.0}
        self.assertEqual(BaseAPI.convert_geom(value), expected)

    def test_convert_geom_from_wkt_string(self):
        value = "POINT (20 10)"
        expected = {"latmin": 10.0, "lonmin": 20.0, "latmax": 10.0, "lonmax": 20.0}
        self.assertEqual(BaseAPI.convert_geom(value), expected)

    def test_convert_geom_invalid_input_raises(self):
        with self.assertRaises(ValueError):
            BaseAPI.convert_geom([200.0, 20.0, 10.0, -20.0])

    def test_make_query_hypernets_constructs_sql(self):
        sql = BaseAPI.make_query_hypernets(
            site_id="GHNA",
            start_time="2022-01-01T00:00:00Z",
            stop_time="2022-01-02T00:00:00Z",
            timeofday_start="08:00:00",
            timeofday_end="12:00:00",
            product_level="L_L2A",
            geom=[10.0, 20.0, 11.0, 21.0],
            only_passed_qc=True,
        )
        self.assertIn("site_id = 'GHNA'", sql)
        self.assertIn("datetime_SEQ>= '2022-01-01 00:00:00'", sql)
        self.assertIn("datetime_SEQ<= '2022-01-02 00:00:00'", sql)
        self.assertIn("product_level = 'L_L2A'", sql)
        self.assertIn("percent_zero_flags>0", sql)
        self.assertFalse(sql.strip().startswith("AND"))


if __name__ == "__main__":
    unittest.main()
