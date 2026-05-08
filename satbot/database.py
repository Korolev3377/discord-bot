# ----- Python Standard Library ----- #
import logging
import os

# ----- Sqlite3 Library ----- #
import sqlite3

Log = logging.getLogger(__name__)

class DataBase:
    def __init__(self, filename="database.db"):
        self.connection = sqlite3.connect(filename)

    def create_table(self, table_name, values):
        self.connection.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({values});")

    def insert(self, table_name, values_expr, values):
        self.connection.execute(f"INSERT INTO {table_name} VALUES ({values_expr});", values)

    def get(self, table_name, where_expr=None):
        if where_expr:
            return self.connection.execute(f"SELECT * FROM {table_name} WHERE {where_expr};")
        else:
            return self.connection.execute(f"SELECT * FROM {table_name};")

if __name__ == "__main__":
    db = DataBase("test.db")
    db.create_table("testTable", "testInt INTENGER PRIMARY KEY, testText TEXT")
    db.insert("testTable", "?, ?", (5, "LOLLOL"))
    print(db.get("testTable").fetchone())