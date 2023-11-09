
import logging
import sqlite3

from webrunit.lib.db.base import DB

def init():
    return SQLite3DB

class SQLite3DB(DB):
    type = "sqlite3"
    conn = None
    cursor = None
    db_path = "webrunit.sqlite3"

    def __init__(self, **kwargs):
        logging.debug("SQLite3DB(%s)" % (kwargs))
        self.__dict__.update(kwargs)
        self.conn = sqlite3.connect( self.db_path, check_same_thread=False )
        self.cursor = self.conn.cursor()
        self.ensure_tables_exist()

    def table_exists(self, name):
        try:
            tables = self.cursor.execute(
                # 'select 1' does not return anything if table is empty
                """SELECT count(1) FROM '%s' LIMIT 1;""" % (name)
            ).fetchall()
        except sqlite3.OperationalError as e:
                message = e.args[0]
                if message.startswith("no such "):
                    return False
                else:
                    raise
        if len(tables) < 1:
            return False
        return True

    def ensure_tables_exist(self):
        if not self.table_exists("jobs"):
            self.cursor.execute(
                """ CREATE TABLE jobs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT
                    ) """
            )


logging.debug("Loaded plugin SQLite3DB()")
