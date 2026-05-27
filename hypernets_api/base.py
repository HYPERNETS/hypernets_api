"""scrappi.api.base - base class for API call handler implementations"""

from abc import ABC, abstractmethod
import datetime
from dateutil.parser import parse
import shapely
import shapely.wkt

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"
__all__ = ["BaseAPI"]


class BaseAPI(ABC):
    """
    Base class for API call handler implementations.
    Subclasses must implement abstract methods.
    """

    def __init__(self):
        pass

    @abstractmethod
    def query(self, *args, **kwargs):
        """
        Return catalogue product url(s) that satisfy query

        :param query: catalogue query
        :return: product urls satisfying query
        """
        pass

    @staticmethod
    def convert_datetime(date_time):
        if isinstance(date_time, datetime.datetime):
            return date_time.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(date_time, datetime.date):
            return date_time.strftime("%Y-%m-%d")
        else:
            if date_time[-1] == "Z":
                date_time = date_time[:-1]
            try:
                return parse(date_time, fuzzy=False).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(
                    "Unable to discern datetime requested: '{}'".format(date_time)
                )

    @staticmethod
    def convert_geom(geom):
        if isinstance(geom, tuple):
            geom = list(geom)
        if isinstance(geom, list):
            if (
                -180 <= geom[1] <= 180
                and -180 <= geom[3] <= 180
                and -90 <= geom[0] <= 90
                and -90 <= geom[2] <= 90
            ):
                return {
                    "latmin": geom[0],
                    "lonmin": geom[1],
                    "latmax": geom[2],
                    "lonmax": geom[3],
                }
            else:
                raise ValueError(
                    """Incorrect "geom" query format. 
                                Please choose from: 
                                    shapely geometry object,
                                    Well-Known-Text string (wkt str)
                                    dict("latmin": val,  "lonmin": val, "latmax": val, "lonmax": val),
                                    list(latmin, lonmin, latmax, lonmax)
                                """
                )
        elif isinstance(geom, dict):
            if {"lonmin", "lonmax", "latmin", "latmax"} == set(geom.keys()):
                return geom
            else:
                raise ValueError(
                    """Incorrect "geom" query format. 
                                Please choose from: 
                                    shapely geometry object,
                                    Well-Known-Text string (wkt str)
                                    dict("latmin": val,  "lonmin": val, "latmax": val, "lonmax": val),
                                    list(latmin, lonmin, latmax, lonmax)
                                """
                )
        elif isinstance(geom, shapely.geometry.Point):
            return {
                    "latmin": geom.y,
                    "lonmin": geom.x,
                    "latmax": geom.y,
                    "lonmax": geom.x,
                }
        elif isinstance(
            geom,
            (
                shapely.geometry.base.BaseGeometry,
                shapely.geometry.base.BaseMultipartGeometry,
            ),
        ):
            return {
                        "latmin": geom.bounds[1],
                        "lonmin": geom.bounds[0],
                        "latmax": geom.bounds[3],
                        "lonmax": geom.bounds[2],
                    }
        else:
            try:
                geom = shapely.wkt.loads(geom)
                return {
                    "latmin": geom.bounds[1],
                    "lonmin": geom.bounds[0],
                    "latmax": geom.bounds[3],
                    "lonmax": geom.bounds[2],
                }
            except shapely.errors.WKTReadingError:
                raise ValueError(
                    """Incorrect "geom" query format. 
                                Please choose from: 
                                    shapely geometry object,
                                    Well-Known-Text string (wkt str)
                                    dict("latmin": val,  "lonmin": val, "latmax": val, "lonmax": val),
                                    list(latmin, lonmin, latmax, lonmax)
                                """
                )

    @staticmethod
    def make_query_hypernets(
        sequence_id=None,
        start_time=None,
        stop_time=None,
        timeofday_start=None,
        timeofday_end=None,
        site_id=None,
        system_id=None,
        product_level=None,
        geom=None,
        only_passed_qc=False
    ):
        if sequence_id:
            cond = "sequence_name = '%s'" %sequence_id

        else:
            if system_id:
                cond = "system_id = '%s'" %system_id

            elif site_id and not site_id == "all":
                cond = "site_id = '%s'" %site_id

            else:
                cond = ""

            if geom:
                geom = BaseAPI.convert_geom(geom)
                cond += " AND latitude >= '%s'"%geom["latmin"]
                cond += " AND longitude >= '%s'"%geom["lonmin"]
                cond += " AND latitude <= '%s'"%geom["latmax"]
                cond += " AND longitude <= '%s'"%geom["lonmax"]

            if start_time:
                cond += " AND datetime_SEQ>= '%s'" % BaseAPI.convert_datetime(start_time)
            if stop_time:
                cond += " AND datetime_SEQ<= '%s'" % BaseAPI.convert_datetime(stop_time)

            if timeofday_start:
                cond += " AND time(datetime_SEQ)>= '%s'" %timeofday_start

            if timeofday_end:
                cond += " AND time(datetime_SEQ)<= '%s'" % timeofday_end

            if product_level:
                cond += " AND product_level = '%s'" % product_level

            if cond[0:4] == " AND":
                cond = cond[4:]

            if only_passed_qc:
                cond += " AND percent_zero_flags>0"

        return (
            "SELECT sequence_name,site_id,system_id,datetime_SEQ,datetime_start,datetime_end,latitude,longitude,product_name,rel_product_dir,product_path FROM products WHERE "
            + cond
            + " ORDER BY datetime_SEQ"
        )


if __name__ == "__main__":
    pass
