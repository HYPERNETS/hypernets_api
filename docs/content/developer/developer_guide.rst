###############
Developer Guide
###############

This guide is for contributors and maintainers of the `hypernets_api` package.
It covers the project layout, testing workflow, documentation build, and
contribution recommendations.

Project layout
--------------

The package lives under `hypernets_api/` and includes the following modules:

- `base.py` — generic helpers for datetime conversion, geometry parsing, and
  SQL query construction
- `offline_api.py` — local archive query implementation using SQLite
- `online_api.py` — STAC search wrapper for LANDHYPERNET
- `stac_client.py` — low-level STAC HTTP client implementation
- `factory.py` — factory class for selecting offline or online APIs

Package metadata, dependencies, and versioning are configured in `pyproject.toml`.
Version management uses `setuptools_scm` with git tags to automatically determine
the package version at build time.

Tests
-----

Unit tests are stored in `hypernets_api/tests`.
Run the test suite from the repository root with:

.. code-block:: bash

   python -m unittest discover -s hypernets_api/tests

Testing focuses on:

- query building and geometry conversion in `BaseAPI`
- archive query and filename lookup behavior in `OfflineHYPERNETSAPI`
- STAC search, item retrieval and downloads in `HYPERNETSAPI`
- HTTP request handling in `LANDHYPERNETSTACClient`
- API selection via `APIFactory`

Documentation
-------------

Documentation content is authored under `docs/content`.
The Sphinx build configuration is located in `docs/conf.py`.

To generate HTML documentation, run:

.. code-block:: bash

   cd docs
   make html

Or use Sphinx directly:

.. code-block:: bash

   sphinx-build -b html . _build/html

The main documentation landing page is `docs/index.rst`, with user-facing
pages under `docs/content/user`.

Development workflow
--------------------

When making changes:

1. Create a branch for your feature or bug fix.
2. Add or update unit tests for new behavior.
3. Update documentation for any public API changes.
4. Run the test suite.
5. Build the documentation to confirm page rendering.

Contribution guidelines
-----------------------

- Keep methods and classes small and focused.
- Provide docstrings for public methods and classes.
- Prefer explicit error handling for invalid query inputs.
- Use `unittest` for new tests and maintain readability.

