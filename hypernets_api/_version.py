"""Package version information for hypernets_api."""

from __future__ import annotations

import os

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

__version__ = "0+unknown"

try:
    __version__ = version("hypernets_api")
except PackageNotFoundError:
    try:
        from setuptools_scm import get_version
    except ImportError:
        pass
    else:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        __version__ = get_version(root=root, relative_to=__file__)
