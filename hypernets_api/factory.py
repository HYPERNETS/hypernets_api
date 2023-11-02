"""scrappi.api.factory - factory to return API call handler classes"""

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"
__all__ = ["APIFactory"]

from hypernets_api.offline_api import OfflineAPI

# plot types by name
API_TYPES = {"offline": OfflineAPI}


class APIFactory:
    def __init__(self):
        self.api_types = API_TYPES

    def get_api(self, name: str):
        """
        Return specified API call handler

        :param name: selected API (e.g. ``"eodag"``)
        :return: reader object
        """

        return self.api_types[name]


if __name__ == "__main__":
    pass
