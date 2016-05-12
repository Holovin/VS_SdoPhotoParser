#!/usr/bin/python
import requests
from database import Database
from error import Error
from donwload import Download
from config import Config
from datetime import datetime

def main():
    db = Database()
    d = Download(db.get_position())
    if not d.auth(Config.USER_NAME, Config.USER_PASS):
        print("[NO ACCESS TO SDO!] Seems like wrong password.")
        exit(0)

    # сделать старт цикла
    res = d.load_user()

    if res is not Error.critical_http and res is not Error.critical_parse:
        if res is not Error.err_not_found:
            user = d.pop_user()
            print(str(datetime.now().time()) + " User: " + user.first_name + " " + user.last_name + " is added;")
            db.insert_user(user)
        db.update_position(d.next())
    else:
        print(str(datetime.now().time()) + " some error... Stopped.")
    # сделать конец цикла


if __name__ == "__main__":
    main()
