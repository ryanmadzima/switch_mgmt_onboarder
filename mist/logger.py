# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Project      : Switch IP Check
# Created By   : Ryan M. Adzima <radzima@juniper.net>
# Created Date : 2021-08-11
# Version      : 0.1
# License      : MIT (see included LICENSE file)
# ------------------------------------------------------------------------------

"""
Logging definition and text coloration class that is used across the entire script
"""

import logging
import sys


class TextColors:
    """
    A simple mapping of colors for colorizing text output
    """
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


logging.basicConfig(stream=sys.stdout, format="[%(levelname)s] -- %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
