
"""The plugin for the Database 'sqlite3'. Defines plugin class and some base functions."""

import sqlite3  # noqa

from palvella.lib.instance.db import DB
from palvella.lib.logging import logging

TYPE = "sqlite3"


class SQLite3DB(DB, class_type="plugin"):
    """
    Class of the SQLite3 database plugin. Inherits the DB class.

    Attributes of this class:
        type            - The name of the type of this database.
        conn            - The handle of a live connection to the database.
        cursor          - The SQLite3 cursor (from 'conn')
    """

    TYPE = TYPE
    conn = None
    cursor = None
    config_data_defaults = {"db_path": "db.sqlite3"}

    def __init__(self, **kwargs):
        """
        Initialize and return new SQLite3DB object.

        When creating a new object, pass arbitrary key=value pairs to update the object.
        After making a successful connection, tables are created if they don't already
        exist.

        Attributes:
          config_data:
            db_path:    - A file path to an SQlite3 database file. If not passed,
                          the default variable 'db_path' in the class is used.
        """

        logging.debug(f"SQLite3DB({kwargs})")
        super().__init__(**kwargs)

    def __pre_plugins__(self):
        self.connect()

    def connect(self):
        """Establish a connection to the SQLite3 database."""
        self.conn = sqlite3.connect(self.config_data['db_path'], check_same_thread=False)
        self.cursor = self.conn.cursor()
        logging.debug(f"DB Connection established to {self.config_data['db_path']}")
        self.ensure_tables_exist()

    def table_exists(self, name):
        """Check if a table exists in the database. Return true if it does, false if it doesn't."""
        try:
            # 'select 1' does not return anything if table is empty.
            # Also, apparently it's illegal to try to paramarerize an 'identifier' like a table name
            # (https://stackoverflow.com/questions/33019599/sqlite-why-cant-parameters-be-used-to-set-an-identifier)
            sql = """SELECT count(1) FROM '%s' LIMIT 1;""" % name
            res = self.cursor.execute(sql)
            tables = res.fetchall()
        except sqlite3.OperationalError as e:
            message = e.args[0]
            if message.startswith("no such table"):
                return False
            raise
        return len(tables) > 0

    def ensure_tables_exist(self):
        """If database tables do not exist in the database yet, create them."""
        if not self.table_exists("jobs_pending"):
            sql = """ CREATE TABLE jobs_pending(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT
                    ) """
            self.cursor.execute(sql)
