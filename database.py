#!/usr/bin/python

import logging
from pymongo import MongoClient
from gridfs import GridFS
from object import Object
from config import Config


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
            keys = {'serverSelectionTimeoutMS': 4000}
            self.client = MongoClient(Config.DB_HOST, Config.DB_PORT)
            self.client.database_names()
            self.db = self.client[Config.DB_NAME]
            logging.info("Connected to mongo... ok")

            self.fs = GridFS(self.db)
            logging.info("GridFS link... ok")

            self.isOperable = True
        except Exception as e:
            logging.fatal("Connection to mongo failed (" + str(e) + ")")
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
            logging.error("Trying insert user in non-valid db!")
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

        logging.info("User [" + str(o.sdo_id) + "] inserted with key: " + str(insert_id))
        return True
