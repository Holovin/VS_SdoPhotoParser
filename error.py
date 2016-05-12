#!/usr/bin/python
from enum import Enum


class Error(Enum):
    critical_http = 1
    critical_parse = 2
    err_not_found = 3
