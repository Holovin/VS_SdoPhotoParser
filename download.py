#!/usr/bin/python

import logging
import requests
from config import Config
from lxml import html
from user import User
from message import Msg


class Download:
    session = None
    current_sdo_id = -1
    last_answer = ""
    last_user_name = ""
    last_user_photo = bytearray()
    last_user_photo_url = ""

    def __init__(self, current):
        self.current_sdo_id = current
        self.session = requests.Session()
        logging.info("Downloader init... ok")
        return

    def auth(self, user_name, user_password):
        o = {
            'username': user_name,
            'password': user_password
        }

        logging.debug("Auth starting...")
        self.last_answer = self.session.post("https://sdo.vsu.by/login/index.php", headers=Config.HEADERS, data=o)

        return self.check_auth(self.last_answer.text)

    @staticmethod
    def check_auth(text):
        if "Неверный логин или пароль, попробуйте заново." in text:
            logging.fatal("Auth failed: bad user/password")
            return False

        if "Вы зашли под именем" in text:
            logging.info("Auth ok...")
            return True

        logging.fatal("Auth unknown state")
        return False

    def clean(self):
        self.last_user_name = ""
        self.last_user_photo = bytearray()
        self.last_user_photo_url = ""
        self.last_answer = ""
        logging.debug("Download: Clean...")

        return

    def load_user(self):
        logging.debug("Load user start...")
        self.clean()

        if not self.get("https://sdo.vsu.by/message/index.php?id=" + str(self.current_sdo_id)):
            logging.fatal("HTTP: cant load profile page")
            return Msg.critical_http

        res = self.parse(self.last_answer.content)

        if res is not Msg.success_ok:
            logging.info("Parse: something wrong...")
            return res

        if not self.photo_parse():
            logging.fatal("HTTP: cant load photo")
            return Msg.critical_http

        logging.debug("Load user... ok")
        return True

    def photo_parse(self):
        if not self.get(self.last_user_photo_url):
            logging.fatal("HTTP: cant load photo (photo_parse)")
            return False

        self.last_user_photo = self.last_answer.content

        logging.debug("Photo parse... ok")
        return True

    def next(self):
        logging.debug("Next user...")
        self.current_sdo_id += 1
        return self.current_sdo_id

    def pop_user(self):
        temp = self.last_user_name.split(' ', 1)

        first_name = "Parse"
        last_name = "Error"

        if len(temp) == 2:
            first_name = temp[0]
            last_name = temp[1]
        else:
            logging.error("Pop user error, parse length is " + str(temp))

        logging.debug("Pop user... ok")
        return User(self.current_sdo_id, first_name, last_name, self.last_user_photo)

    def parse(self, content):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        error_status_not_found = tree.xpath('//p[@class="errormessage"]/text()')
        error_status_removed = tree.xpath('//div[contains(text(),"Некорректный пользователь")]')

        if len(error_status_not_found) > 0 or len(error_status_removed) > 0:
            self.last_user_name = "Wrong user ID"
            self.last_user_photo_url = ""
            logging.error("Parse error: wrong user id (" + str(error_status_not_found) + ") or (" +
                          str(error_status_removed) + ")")

            return Msg.err_not_found

        temp_name = tree.xpath('//td[@id="user2"]/div[@class="heading"]/text()')
        temp_photo_url = tree.xpath('//td[@id="user2"]/a/img/@src')

        if len(temp_name) < 1 or len(temp_photo_url) < 1:
            logging.debug("Parser: Empty user")
            return Msg.critical_parse

        self.last_user_name = temp_name[0]
        self.last_user_photo_url = temp_photo_url[0]
        logging.debug("Parser: " + self.last_user_name)

        return Msg.success_ok

    def get(self, url):
        logging.debug("Getting url: " + url)
        try:
            self.last_answer = self.session.get(url, headers=Config.HEADERS)

        except requests.exceptions.RequestException as e:
            logging.fatal("Fatal error (get_url: " + url + "): " + str(e))
            return False

        logging.debug("Getting url... ok")
        return True
