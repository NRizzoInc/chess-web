#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os, sys
import argparse # cli paths
import datetime
from typing import Optional, Dict, List

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import pymysql

#--------------------------------Project Includes--------------------------------#

class DB_Manager():
    def __init__(self, user:str, pwd:str, db:str, host:str):
        """
            \n@param: user  - The username to connect to database with
            \n@param: pwd   - The password to connect to database with
            \n@param: db    - The name of the database to connect with
            \n@param: host  - The IP/localhost of the database to connect with
            \nNote: This class defines all functions not specific to the Reader or Mobile App
        """
        self._host = host
        self._user = user
        self._pwd = pwd
        self._db = db
        try:
            # self.connect_db()
            pass
        except Exception as err:
            raise SystemExit(f"Invalid Database Login: {err}")


    def connect_db(self):
        """Creates self.conn & self.cursor objects"""
        self.conn = pymysql.connect(
            host=self._host,
            user=self._user,
            password=self._pwd,
            db=self._db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def cleanup(self):
        self.cursor.close()
        self.conn.close()

    def check_conn(self):
        """Decorator to check if need to reconnect to db & does so if needed"""
        # check if youre connected, if not, connect again
        self.conn.ping(reconnect=True)
        self.cursor = self.conn.cursor()

    def updatePwd(self):
        "WIP"
        pass

    def add_user(self, fname:str, lname:str, username:str, pwd:str) -> int:
        """Creates a new database entry for a user and returns its unique id.

        Returns:
            int: The id of the newly created user (-1 if error)
        """
        self.check_conn()
        try:
            self.cursor.execute("call add_user(%s, %s, %s, %s)",
                (fname, lname, username, pwd))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"add_car error: {err}")
            return -1

    def does_username_exist(self, uname: str) -> bool:
        self.check_conn()
        try:
            self.cursor.execute("call does_username_exist(%s)", (uname))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"does_username_exist error: {err}")
            return -1

    def get_user_id(self, uname) -> int:
        """:returns the user_id of user with 'username' (-1 on error)"""
        self.check_conn()
        try:
            self.cursor.execute("select get_user_id(%s)", uname)
            user_ids = list(self.cursor.fetchone().values())[0]
            # use '.values()' to make python agnostic to the name of returned col in procedure
            # return user_ids[0].values()[0] if len(user_ids) > 0 else -1
            return user_ids if user_ids is not None else -1
        except:
            return -1

    def update_pwd(self, uname: str, pwd: str) -> bool:
        """:returns -1 on error, 1 on success"""
        self.check_conn()
        try:
            self.cursor.execute("call update_pwd(%s, %s)", (uname, pwd))

            # ignore name of field and just get the value
            return 1
        except Exception as err:
            print(f"update_pwd error: {err}")
            return -1

    def check_password(self, uname: str, pwd: str) -> bool:
        """Returns True if password and username are valid to login"""
        self.check_conn()
        try:
            self.cursor.execute("call check_password(%s, %s)", (uname, pwd))

            # ignore name of field and just get the value
            return list(self.cursor.fetchall()[0].values())[0]
        except Exception as err:
            print(f"check_password error: {err}")
            return -1

