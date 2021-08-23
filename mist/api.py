# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Project      : Switch IP Check
# Created By   : Ryan M. Adzima <radzima@juniper.net>
# Created Date : 2021-08-11
# Version      : 0.1
# License      : MIT (see included LICENSE file)
# ------------------------------------------------------------------------------

"""
Mist API class definition for interacting with the Mist cloud
"""

from typing import Dict, List, Union
from http.client import HTTPSConnection
import json
from .logger import logger, TextColors


class API:
    """
    Mist API class definition for interacting with the Mist cloud
    """

    org_id: str
    token: str

    def __init__(self, org_id: str, token: str):
        """
        Initialize the API object

        :param str org_id: Mist organization identifier string
        :param str token: Mist API authentication token
        """
        self.org_id = org_id
        self.token = token

    @property
    def headers(self) -> Dict:
        """
        Calculated property that constructs the appropriate authentication headers for interacting with the Mist cloud

        :return dict: A dictionary containing the Authorization token and Content-type
        """
        try:
            h = {
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Unable to build headers:{TextColors.ENDC} {e}")
            raise e
        return h

    def get(self, host: str, endpoint: str) -> Union[Dict, List]:
        """
        Process an HTTPS request to a given host and endpoint

        :param str host: The host FQDN or IP (e.g. api.mist.com)
        :param str endpoint: The API endpoint located at the host (e.g. /api/v1/self)
        :return Union[Dict,List]: A dictionary or list containing the JSON response data
        """
        try:
            conn = HTTPSConnection(host=host)
            conn.request(method="GET", url=endpoint, headers=self.headers)
            res = conn.getresponse()
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Error getting data from '{TextColors.WARNING}{host}{TextColors.FAIL}' at '{TextColors.WARNING}{endpoint}{TextColors.FAIL}'{TextColors.ENDC}")
            raise e
        try:
            response = json.loads(res.read().decode())
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Error parsing JSON response:{TextColors.ENDC} {e}")
            raise e
        return response
