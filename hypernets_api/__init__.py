"""hypernets_api - API to access hypernets data"""

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"
__all__ = ["HYPERNETSAPI", "OfflineHYPERNETSAPI"]

from ._version import __version__

from hypernets_api.online_api import HYPERNETSAPI
from hypernets_api.offline_api import OfflineHYPERNETSAPI   