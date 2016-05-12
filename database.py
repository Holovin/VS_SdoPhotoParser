#!/usr/bin/python

from pymongo import MongoClient
from gridfs import GridFS
from user import User
from object import Object

class Database:
    client = None
    db = None
    fs = None
    isOperable = False

    position_selector = {
        'key': 'position'
    }

    def __init__(self):
        try:
            keys = {"serverSelectionTimeoutMS": 4000}
            self.client = MongoClient('127.0.0.1', 27017)
            self.client.database_names()
            self.db = self.client['sdo_photos']
            self.fs = GridFS(self.db)
            self.isOperable = True
        except:
            print("Cannot connect to MongoDB.")
            self.isOperable = False
        return

    def get_position(self):
        return self.db['settings'].find_one(self.position_selector)['value']

    def update_position(self, position):
        up = {
            '$set': {
                'value': position
            }
        }

        self.db['settings'].update_one(self.position_selector, up)
        return

    def insert_user(self, user):
        if not self.isOperable:
            return False

        photo_id = None

        if (user.photo is not None) and (len(user.photo) > 0):
            photo_id = self.fs.put(user.photo, filename=str(user.sdo_id) + ".png")

        o = Object()
        o.first_name = user.first_name
        o.last_name = user.last_name
        o.sdo_id = user.sdo_id
        o.photo_grid_fs_id = photo_id

        insert_id = self.db['users'].insert_one(o.__dict__).inserted_id

        print(">>>         >>> Inserted with key: " + str(insert_id))

        return True
