import sqlite3 as sql
from typing import Any, Union

from discord.app_commands import Choice

from environment.variable import *


class DataBase:
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.users = None
        self.connect()
        self.disconnect()

    def connect(self):
        self.db_connection = sql.connect("database.db")
        self.db_cursor = self.db_connection.cursor()
        self.db_cursor.execute("SELECT name, id FROM users WHERE is_visible = 1;")
        i = self.db_cursor.fetchall()
        dat = []
        if i:
            for _ in i:
                dat.append(Choice(name=str(_[0]), value=str(_[1])))
            self.users = dat
        else:
            self.users = None

    def disconnect(self):
        self.db_connection.commit()
        self.db_connection.close()

    def execute(self, q: str, arg: tuple = None, fetchone: bool = True) -> Union[tuple, bool]:
        self.db_cursor.execute(q, arg) if arg else self.db_cursor.execute(q)
        i = self.db_cursor.fetchone() if fetchone else self.db_cursor.fetchall()
        return i or False


DB = DataBase()
