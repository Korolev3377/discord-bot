import sqlite3 as sql
from typing import Any, Union, NoReturn

from discord.app_commands import Choice

from environment.variable import *


class DataBase:
    def __init__(self) -> None:
        self.db_connection = None
        self.db_cursor = None
        self.connect()
        self.disconnect()

    def connect(self) -> NoReturn:
        self.db_connection = sql.connect("database.db")
        self.db_cursor = self.db_connection.cursor()

    def disconnect(self) -> NoReturn:
        self.db_connection.commit()
        self.db_connection.close()

    def execute(self, q: str, arg: tuple = None, fetchone: bool = True) -> Union[tuple, bool]:
        self.db_cursor.execute(q, arg) if arg else self.db_cursor.execute(q)
        i = self.db_cursor.fetchone() if fetchone else self.db_cursor.fetchall()
        return i or False


DB = DataBase()
