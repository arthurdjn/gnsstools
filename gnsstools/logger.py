# File: logger.py
# Creation: Friday January 22nd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


r"""
This module handles logs using the ``logging`` package.

"""

# Basic imports
import logging


logging.basicConfig(
    filename="gnss_toolbox.log",
    filemode="a",
    format="%(asctime)s :: %(name)-20s :: [%(filename)-10s:%(lineno)-3s - %(funcName)20s()] :: [%(levelname)-7s] :: %(message)s",
    level=logging.DEBUG
)

logger = logging.getLogger("gnss_toolbox")