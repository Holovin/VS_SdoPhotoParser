#!/usr/bin/python
from enum import Enum


class Msg(Enum):
    success_ok = 1
    critical_http = 2
    critical_parse = 3
    err_not_found = 4
