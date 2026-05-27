.. _atbd:

#########################################
Algorithm Theoretical Basis Documentation
#########################################

This document describes the conceptual design and data model used by the
`hypernets_api` package. It explains the two supported access modes:

- local offline archive queries via `OfflineHYPERNETSAPI`
- online STAC queries via `HYPERNETSAPI`

Overview
--------

`hypernets_api` provides a unified interface for discovering and retrieving
HYPERNETS products. The package supports both local archive access and
remote STAC search, enabling users to choose the workflow that best matches
their data environment.

Data model
----------

The package is based on two complementary data models:

- an offline SQLite archive stored locally
- the LANDHYPERNET STAC catalogue accessed over HTTP

Offline mode uses an internal SQL query builder to translate user query
parameters into `SELECT` statements against the `products` table in the
archive database.
Online mode builds STAC query parameters, authenticates with a bearer token,
and performs search requests against the HYPERNETS STAC API.

Offline archive architecture
----------------------------

`OfflineHYPERNETSAPI` expects a directory containing an archive database and
product files. The key metadata fields are:

- `sequence_name`
- `site_id`
- `system_id`
- `datetime_SEQ`
- `datetime_start`
- `datetime_end`
- `latitude`
- `longitude`
- `product_name`
- `rel_product_dir`
- `product_path`

The package normalises file path separators from the archive database to the
current operating system, so query results are consistent across platforms.

Query semantics
---------------

The offline query builder in `BaseAPI.make_query_hypernets` supports:

- spatial bounding boxes
- time range filtering
- product level matching
- quality control filtering
- site and system selection

Geometry can be supplied as a list, tuple, dictionary, Shapely geometry,
or a WKT string. This flexibility allows integration with both numeric
filters and geospatial workflows.

Product level normalization
---------------------------

Offline and online workflows use a common product level vocabulary. The
package maps shorthand collection names to canonical archive values where
required, for example:

- `L2A` -> `L_L2A`
- `L2B` -> `L_L2B`
- `L1B_RAD` -> `L_L1B_RAD`

This mapping ensures that user queries are accepted even when the underlying
archive metadata uses a different level naming convention.

Online STAC architecture
------------------------

`HYPERNETSAPI` is a thin wrapper around `LANDHYPERNETSTACClient`.
The STAC client handles:

- token management
- root catalog discovery
- collections listing
- search requests
- asset downloads
- item retrieval by sequence name

Search requests use standard STAC parameters such as `bbox`, `datetime`, and
`limit`, with additional support for site and product level filters.

