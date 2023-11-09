
import sqlite3

from webrunit.lib.logging import logging as logging
from webrunit.lib.db.base import DB

type = "sqlite3"

class SQLite3DB(DB):
    """ Class of the SQLite3 database plugin.
        Inherits the DB class.

        Attributes of this class:
            'type'      - The name of the type of this database.
            'conn'      - The handle of a live connection to the database.
            'cursor'    - The SQLite3 cursor (from 'conn')
            'db_path'   - The default file path to the default SQLite3 database.
    """

    type = type
    conn = None
    cursor = None
    db_path = "webrunit.sqlite3"

    def __init__(self, **kwargs):
        """ When creating a new object, pass arbitrary key=value pairs to update the object.
            The following are used:
                'db_path':string        - A file path to an SQlite3 database file. If not passed,
                                          the default variable 'db_path' in the class is used.

            After making a successful connection, tables are created if they don't already
            exist.
        """
        logging.debug("SQLite3DB(%s)" % (kwargs))
        self.__dict__.update(kwargs)
        self.conn = sqlite3.connect( self.db_path, check_same_thread=False )
        self.cursor = self.conn.cursor()
        logging.debug("DB Connection established to {}".format(self.db_path))
        self.ensure_tables_exist()

    def table_exists(self, name):
        """ Checks if a table exists in the database. 
            Returns true if it does, false if it doesn't.
        """
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
        """ If database tables do not exist in the database yet, create them. """

        if not self.table_exists("jobs"):
            self.cursor.execute(
                """ CREATE TABLE jobs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT
                    ) """
            )

classref = SQLite3DB # Used by base class to load a new plugin class object
logging.debug("Loaded plugin SQLite3DB()")
