.. _quickstart:

################
Quickstart Guide
################

This quickstart introduces the core `hypernets_api` workflows for both local
archive access and remote STAC discovery.

Installation
------------

Install the package from PyPI:

.. code-block:: bash

   pip install hypernets_api

For development installation with extras:

.. code-block:: bash

   pip install -e ".[dev]"

Overview
--------

`hypernets_api` exposes two main APIs:

- `OfflineHYPERNETSAPI`: query local HYPERNETS archive metadata and file paths
- `HYPERNETSAPI`: search the LANDHYPERNET STAC API and retrieve assets

A factory helper, `APIFactory`, can be used to select the offline or online
implementation by name.

Offline usage example
---------------------

Use `OfflineHYPERNETSAPI` when you have a local archive database and product
files.

.. code-block:: python

   from hypernets_api.offline_api import OfflineHYPERNETSAPI

   archive_path = "/path/to/archive"
   archive_db = "archive.db"
   data_path = "/path/to/archive"

   api = OfflineHYPERNETSAPI(
       archive_path,
       archive_db=archive_db,
       data_path=data_path,
   )

   query = {
       "site": "GHNA",
       "start_time": "2022-06-17T09:00:00",
       "stop_time": "2022-06-17T11:00:00",
       "product_level": "L2B",
   }

   results = api.query(query)
   print(results)

Lookup a specific file name:

.. code-block:: python

   file_path = api.query_filename("example_product.nc")
   print(file_path)

Online usage example
--------------------

Use `HYPERNETSAPI` to search the LANDHYPERNET STAC portal.

.. code-block:: python

   from hypernets_api.online_api import HYPERNETSAPI

   api = HYPERNETSAPI(api_token="YOUR_TOKEN")

   query = {
       "site": "GHNA",
       "product_level": "L2B",
       "start_time": "2022-06-01",
       "stop_time": "2022-06-30",
   }

   results = api.query(query)
   print(results)

Download assets from results:

.. code-block:: python

   api.download_results(results, output_path="/tmp/hypernets")

