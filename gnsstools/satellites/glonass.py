# File: glonass.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


from .satellite import Satellite


class GLONASS(Satellite):
    
    def __init__(self):
        super().__init__()