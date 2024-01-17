
"""The plugin for the Database 'sqlite3'. Defines plugin class and some base functions."""

import sqlite3  # noqa

from palvella.lib.instance.db import DB

PLUGIN_TYPE = "sqlite3"


class SQLite3DB(DB, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """
    Class of the SQLite3 database plugin. Inherits the DB class.

    Attributes of this class:
        type            - The name of the type of this database.
        conn            - The handle of a live connection to the database.
        cursor          - The SQLite3 cursor (from 'conn')
    """

    conn = None
    cursor = None

    def __pre_plugins__(self):
        self.connect()

    def connect(self):
        """Establish a connection to the SQLite3 database."""
        self.conn = sqlite3.connect(self.config_data['db_path'], check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.logger.debug(f"DB Connection established to {self.config_data['db_path']}")
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
