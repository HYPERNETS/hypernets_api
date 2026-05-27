###########
User Guide
###########

This guide describes how to use `hypernets_api` to discover and access
HYPERNETS products from either a local archive or the LANDHYPERNET STAC portal.

The sections below explain the package architecture, query options, and
examples for common workflows.

Introduction
------------

`hypernets_api` is a lightweight Python package for querying HYPERNETS data.
It supports two modes of operation:

- `OfflineHYPERNETSAPI`: query a local archive database and product files
- `HYPERNETSAPI`: query the LANDHYPERNET STAC service and download assets

The package is intentionally minimal and focuses on exposing a consistent API
for both local and online discovery.

Package structure
-----------------

Important modules include:

- `hypernets_api.base`: shared utility functions and query builders
- `hypernets_api.offline_api`: local archive query implementation
- `hypernets_api.online_api`: STAC-based online search client
- `hypernets_api.stac_client`: lower-level STAC request client
- `hypernets_api.factory`: helper to select API implementations

Online STAC usage
-----------------

The online API uses a bearer token to authenticate against the LANDHYPERNET
STAC service. It performs searches and downloads assets from the STAC
endpoint.

Example: authenticated search

.. code-block:: python

   from hypernets_api.online_api import HYPERNETSAPI

   api = HYPERNETSAPI(api_token="YOUR_TOKEN")
   query = {
       "site": "GHNA",
       "product_level": "L2A",
       "start_time": "2022-06-01",
       "stop_time": "2022-06-30",
   }
   results = api.query(query)
   print(len(results.get("features", [])))

Example: retrieve a specific sequence

.. code-block:: python

   item = api.query_sequence("sequence_1", "L2A")
   print(item)

Example: download matched assets

.. code-block:: python

   api.download_results(results, output_path="/tmp/hypernets")

Query options
-------------

The online query supports these fields:

- `site`, `site_id`: site identifier for the search
- `geom`: bounding box for spatial filtering
- `product_level`, `collection`, `level`: product collection identifier
- `start_time`, `stop_time`: lower and upper date bounds
- `datetime`: explicit STAC datetime range string

If `datetime` is omitted, the package combines `start_time` and `stop_time`
in a single range string.

Offline archive usage
---------------------

The offline API is useful when you have a local HYPERNETS archive.
It requires an archive path and a local SQLite database file.

`OfflineHYPERNETSAPI` supports the following query parameters:

- `site`: site identifier, for example `GHNA`
- `geom`: spatial bounding box or geometry object
- `start_time`: start timestamp for `datetime_SEQ`
- `stop_time`: end timestamp for `datetime_SEQ`
- `product_level`: product level code, such as `L_L2A`
- `only_passed_qc`: boolean to filter results by quality control

Spatial queries accept either:

- bounding box dictionaries
- `shapely` geometries
- Well-Known Text strings
- lists or tuples of `[latmin, lonmin, latmax, lonmax]`

Example: query by site and time range

.. code-block:: python

   from hypernets_api.offline_api import OfflineHYPERNETSAPI

   api = OfflineHYPERNETSAPI("/data/archive", archive_db="archive.db")
   query = {
       "site": "GHNA",
       "start_time": "2022-06-17T09:00:00",
       "stop_time": "2022-06-17T11:00:00",
       "product_level": "L_L2A",
   }
   results = api.query(query)
   for item in results:
       print(item["product_path"])

Example: query by geometry

.. code-block:: python

   query = {
       "geom": {
           "latmin": 51.7763,
           "lonmin": -1.3399,
           "latmax": 51.7780,
           "lonmax": -1.3370,
       },
       "product_level": "L_L2A",
   }
   results = api.query(query)

Finding a file by name
----------------------

`OfflineHYPERNETSAPI.query_filename(filename)` searches the archive directory
structure for a unique match. It raises an error if no file is found or multiple
files are found.


Best practices
--------------
- Use the offline API when you need fast local lookups and have a local copy of
  the archive.
- Use the online API when you need current catalog discovery from LANDHYPERNET.
- Provide `data_path` to `OfflineHYPERNETSAPI` when you want result paths to be
  rewritten relative to local storage.
- Always verify the STAC `api_token` before making search requests.

Troubleshooting
---------------

- `ValueError: The archive path does not exists` means the local archive path is
  incorrect or missing.
- `ValueError: no data found between the specified dates` indicates the query
  returned an empty archive result set.
- If online searches fail, confirm that the API token is present and valid.

.. toctree::
   :maxdepth: 2
   :hidden:

   quickstart
