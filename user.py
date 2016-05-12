#!/usr/bin/python


class User:
    sdo_id = -1
    photo = bytearray()
    first_name = ""
    last_name = ""

    def __init__(self, sdo_id, first_name="", last_name="", photo=""):
        self.sdo_id = sdo_id
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo
        return
