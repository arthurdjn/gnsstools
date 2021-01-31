# Encoding: UTF-8
# File: utils.py
# Creation: Saturday January 30th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
import re


def camel2snake(string):
    compiled = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
    # For case like "dX2" -> "dx2"
    if string[0] == "d" and string[1].isupper():
        return "d" + compiled.sub(r'_\1', string[1:]).lower()
    # For camel case
    return compiled.sub(r'_\1', string).lower()
