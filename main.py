#!/usr/bin/python

import logging
from database import Database
from message import Msg
from download import Download
from config import Config
from time import sleep


def main():
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

    db = Database()
    pos = db.get_position()
    d = Download(pos)
    if not d.auth(Config.USER_NAME, Config.USER_PASS):
        logging.fatal("No access to SDO, exit...")
        exit(0)

    logging.info("Starting from: " + str(pos))
    while True:
        res = d.load_user()

        if res is not Msg.critical_http and res is not Msg.critical_parse:
            if res is not Msg.err_not_found:
                user = d.pop_user()
                logging.info("User " + user.first_name + " " + user.last_name + " added")
                db.insert_user(user)
            else:
                logging.info("Wrong user id, skipped...")
            db.update_position(d.next())
            sleep(0.3)
        else:
            logging.fatal("Some fatal error, exit...")
            break

    logging.info("--- APP END ---")


if __name__ == "__main__":
    main()
