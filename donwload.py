#!/usr/bin/python

import requests
from lxml import html
from user import User
from error import Error


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
        return

    def auth(self, user_name, user_password):
        o = {
            'username': user_name,
            'password': user_password
        }

        self.last_answer = self.session.post("https://sdo.vsu.by/login/index.php", data=o)

        return self.check_auth(self.last_answer.text)

    @staticmethod
    def check_auth(text):
        # Не лучшая проверка, да
        if "Неверный логин или пароль, попробуйте заново." in text:
            return False

        if "Вы зашли под именем" in text:
            return True

        return False

    def clean(self):
        self.last_user_name = ""
        self.last_user_photo = bytearray()
        self.last_user_photo_url = ""
        self.last_answer = ""

        return

    def load_user(self):
        self.clean()

        if not self.get("https://sdo.vsu.by/message/index.php?id=" + str(self.current_sdo_id)):
            return Error.critical_http

        res = self.parse(self.last_answer.content)

        if res is not True:
            return res

        if not self.photo_parse():
            return Error.critical_http

        return True

    def photo_parse(self):
        if not self.get(self.last_user_photo_url):
            return False

        self.last_user_photo = self.last_answer.content

        return True

    def next(self):
        self.current_sdo_id += 1
        return self.current_sdo_id

    def pop_user(self):
        temp = self.last_user_name.split(' ', 1)

        first_name = "Parse"
        last_name = "Error"

        if len(temp) == 2:
            first_name = temp[0]
            last_name = temp[1]

        return User(self.current_sdo_id, first_name, last_name, self.last_user_photo)

    def parse(self, content):
        tree = html.fromstring(content)

        # if tree.xpath('//p[@class="errormessage"]/text()') != "":
        #     self.last_user_name = "Wrong user ID"
        #     self.last_user_photo_url = ""
        #     return Error.err_not_found

        temp_name = tree.xpath('//td[@id="user2"]/div[@class="heading"]/text()')
        temp_photo_url = self.last_user_photo_url = tree.xpath('//td[@id="user2"]/a/img/@src')

        if len(temp_name) < 1 or len(temp_photo_url) < 1:
            return Error.critical_parse

        self.last_user_name = temp_name[0]
        self.last_user_photo_url = temp_photo_url[0]

        return True

    def get(self, url):
        try:
            self.last_answer = self.session.get(url)

        except requests.exceptions.RequestException as e:
            # protection for list and other "buggest" vars
            print('Fatal error at url: ')
            print(url)
            print(e)
            return False

        return True
