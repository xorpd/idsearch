import logging
import os
import sqlite3
from .exceptions import GenDBError
from .types import XrefTypes, LineTypes, data_to_hex, hex_to_data

logger = logging.getLogger(__name__)

def get_enum_opts(enum):
    """
    Get all options of an enum
    """
    opts = []
    for attr_name in enum.__dict__:
        if not attr_name.startswith('_'):
            opts.append(attr_name)
    return opts



class SDBGen(object):
    def __init__(self,sdb_path):
        self._sdb_path = sdb_path
        if sdb_path != ':memory:':
            if os.path.isfile(sdb_path):
                raise GenDBError('File already exists. Aborting.')

        self._conn = sqlite3.connect(self._sdb_path,isolation_level=None)

        self._create_enum_tables()
        self._create_main_tables()
        self._create_indexes()

    def _create_enum_tables(self):
        """
        Create enum tables: line_types and xref_types
        """
        # Create line types enum table:
        self._conn.execute("""CREATE TABLE line_types (
            id INTEGER PRIMARY KEY)""")

        for opt in get_enum_opts(LineTypes):
            line_type = getattr(LineTypes,opt)
            self._conn.execute(
                'INSERT into line_types (id) VALUES (?)',(line_type,))

        # Create xref types enum table:
        self._conn.execute("""CREATE TABLE xref_types (
            id INTEGER PRIMARY KEY)""")

        for opt in get_enum_opts(XrefTypes):
            xref_type = getattr(XrefTypes,opt)
            self._conn.execute(
                'INSERT into xref_types (id) VALUES (?)',(xref_type,))


    def _create_main_tables(self):
        """
        Create search database from given idb.
        """

        # Create table of functions:
        #   - name
        #   - start (id)
        #   - end

        self._conn.execute("""CREATE TABLE funcs (
            address INTEGER PRIMARY KEY,
            name TEXT NOT NULL)""")

        self._conn.execute("""CREATE TABLE lines (
            address INTEGER PRIMARY KEY,
            type REFERENCES line_types(id),
            line_text_hex TEXT NOT NULL,
            line_data_hex TEXT)""")

        # Create External content table:
        # See 6.2.2 in sqlite fts3.html documentation.
        self._conn.execute("""CREATE VIRTUAL TABLE lines_text_fts USING fts4(
            content="lines",  line_text_hex)""")

        self._conn.execute("""CREATE VIRTUAL TABLE lines_text_tokens_fts USING fts4(
            content="lines",  line_text)""")

        self._conn.execute("""CREATE VIRTUAL TABLE lines_data_fts USING fts4(
            content="lines", line_data_hex)""")

        self._conn.execute("""CREATE TABLE funcs_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line REFERENCES lines(address),
            func REFERENCES funcs(address))""")

        self._conn.execute("""CREATE TABLE xrefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            xref_type REFERENCES xref_types(id),
            line_from REFERENCES lines(id),
            line_to REFERENCES lines(id))""")

    def _create_indexes(self):
        """
        Create search relevant search indexes.
        """
        self._conn.execute('CREATE INDEX index_line_from ON xrefs(line_from)')
        self._conn.execute('CREATE INDEX index_line_to ON xrefs(line_to)')
        self._conn.execute('CREATE INDEX index_line_address ON '
            'funcs_lines(line)')
        self._conn.execute('CREATE INDEX index_func_address ON '
            'funcs_lines(func)')

        # Avoid duplication of rows in xrefs:
        self._conn.execute('CREATE UNIQUE INDEX index_xrefs ON '
            'xrefs(xref_type,line_from,line_to)')
        # Avoid duplication of rows in line_func:
        self._conn.execute('CREATE UNIQUE INDEX line_func ON '
            'funcs_lines(line,func)')


    def begin_transaction(self):
        """
        Begin a transaction.
        """
        self._conn.execute('BEGIN TRANSACTION')

    def commit_transaction(self):
        """
        Commit a transaction
        """
        try:
            self._conn.execute('COMMIT')
        except sqlite3.Error:
            self._conn.execute('ROLLBACK')
            raise GenDBError('Failed to commit transaction')

    def add_line(self,addr,line_type,line_text,line_data):
        """
        Returns line id
        """
        # Convert line data to hex:
        line_data_hex = data_to_hex(line_data)
        line_text_hex = data_to_hex(line_text)

        self._conn.execute("""INSERT INTO lines 
            (address,type,line_text_hex,line_data_hex) VALUES
            (?, ?, ?, ?)""",(addr,line_type,line_text_hex,line_data_hex,))

    def add_xref(self,xref_type,line_from,line_to):
        """
        Returns xref id
        """
        self._conn.execute("""INSERT INTO xrefs (xref_type,line_from,line_to)
            VALUES (?, ?, ?)""",(xref_type,line_from,line_to,))

    def add_function(self,address,name,line_addresses):
        """
        Add a function. line_addresses are the addresses of all the lines that
        belong to the function.
        """
        # Insert function:
        self._conn.execute("""INSERT INTO funcs (address,name)
            VALUES (?, ?)""",(address,name,))

        # Insert all func_line connections:
        for line_addr in line_addresses:
            self._conn.execute("""INSERT INTO funcs_lines (line,func)
                VALUES (?, ?)""",(line_addr,address,))

    def fill_lines_fts(self):
        """
        Fill in the fts index for the lines table.
        Should be called after no more insertions are expected.
        """
        self._conn.execute("""INSERT INTO lines_text_fts(
            rowid,line_text_hex) SELECT 
            address, line_text_hex FROM lines""")

        rows = self._conn.execute(
            """SELECT address,line_text_hex FROM lines""").fetchall()

        # Converting all hexified line text back to the real text, to allow
        # quick token based fts search:
        self.begin_transaction()
        for row in rows:
            self._conn.execute("""INSERT INTO lines_text_tokens_fts(
                rowid,line_text) VALUES (?,?)""",(row[0],hex_to_data(row[1])))
        self.commit_transaction()

        self._conn.execute("""INSERT INTO lines_data_fts(
            rowid,line_data_hex) SELECT 
            address, line_data_hex FROM lines""")

    def close(self):
        """
        Close connection to database.
        """
        self._conn.close()
