# Encoding: UTF-8
# File: rinex.py
# Creation: Monday January 25th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
from abc import ABC


class RinexReader(ABC):
    
    def __init__(self):
        super().__init__()
        
    