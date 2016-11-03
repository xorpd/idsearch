import os
from .usqlite3 import sqlite3
from .exceptions import SearchDBError
from .types import hex_to_data, data_to_hex,\
    Xref, Line, Function


def ident_iter_proxy(input_iter):
    """
    The identity iterator proxy.
    yields the exact same elements from the input iterator.
    """
    for elem in input_iter:
        yield elem

class SearchDB(object):
    def __init__(self,sdb_path,iter_proxy=ident_iter_proxy):
        self._sdb_path = sdb_path
        self._iter_proxy = iter_proxy
        if not os.path.isfile(sdb_path):
            raise SearchDBError('SearchDB {} Does not exist'\
                    .format(sdb_path))

        self._conn = sqlite3.connect(self._sdb_path)

    def all_lines(self):
        """
        Return all lines
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,
            line_data_hex FROM lines""")

        return self._iter_proxy(
                (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3])) 
                    for row in rows))

    def all_functions(self):
        """
        Return all functions
        """
        rows = self._conn.execute("""SELECT address,name FROM funcs""")
        return self._iter_proxy((Function(row[0],row[1]) for row in rows))

    def all_xrefs(self):
        """
        Return all xrefs
        """
        rows = self._conn.execute(
                'SELECT xref_type, line_from, line_to FROM xrefs ')

        return self._iter_proxy((Xref(row[0],row[1],row[2]) for row in rows))


    def xrefs_to(self,line_to):
        """
        Get addresses of all lines that xref to <line_to>
        """
        rows = self._conn.execute(
                'SELECT xref_type, line_from, line_to FROM xrefs '
                'WHERE line_to = ?', (line_to,))

        return self._iter_proxy((Xref(row[0],row[1],row[2]) for row in rows))

    def xrefs_from(self,line_from):
        """
        Get addresses to all lines that are xrefed from <line_from>
        """
        rows = self._conn.execute(
                'SELECT xref_type, line_from, line_to FROM xrefs '
                'WHERE line_from = ?', (line_from,))

        return self._iter_proxy((Xref(row[0],row[1],row[2]) for row in rows))


    def get_line(self,line_address):
        """
        Get line by line address
        """
        row = self._conn.execute(
                'SELECT address, type,line_text_hex,line_data_hex FROM lines '
                'WHERE address = ?', (line_address,)).fetchone()

        if row is None:
            raise SearchDBError('Line of address {} is not in sdb'\
                    .format(address))

        return Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3]))


    def lines_in_func(self,func_addr):
        """
        Return the addresses of all lines 
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,line_data_hex 
            FROM lines INNER JOIN  funcs_lines ON 
            lines.address = funcs_lines.line WHERE funcs_lines.func = ?""",
            (func_addr,))

        return self._iter_proxy(
                (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3]))
                    for row in rows))


    def funcs_by_line(self,line_address):
        """
        Return all functions that contain a line.
        """
        rows = self._conn.execute("""SELECT address,name 
            FROM funcs INNER JOIN  funcs_lines ON 
            funcs.address = funcs_lines.func 
            WHERE funcs_lines.line = ?""",
            (line_address,))

        return self._iter_proxy((Function(row[0],row[1]) for row in rows))

    def match_text_fts(self,match_query):
        """
        Return all lines that match a certain match_query
        Supports fts4 query syntax.
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,
            line_data_hex FROM lines WHERE address IN 
            (SELECT rowid from lines_text_fts WHERE lines_text_fts MATCH ?)""",
            (match_query,))

        return self._iter_proxy(
                (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3])) 
                    for row in rows))

    def match_text_tokens_fts(self,match_query):
        """
        Return all lines that match a certain match_query
        Supports fts4 query syntax.
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,
            line_data_hex FROM lines WHERE address IN 
            (SELECT rowid from lines_text_tokens_fts 
            WHERE lines_text_tokens_fts MATCH ?)""",
            (match_query,))

        return self._iter_proxy(
                (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3])) 
                    for row in rows))

    def match_data_fts(self,match_query):
        """
        Return all lines that match a certain match_query
        Supports fts4 query syntax.
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,
            line_data_hex FROM lines WHERE address IN 
            (SELECT rowid from lines_data_fts WHERE lines_data_fts MATCH ?)""",
            (match_query,))

        return self._iter_proxy(
            (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3])) 
                for row in rows))

    def lines_text(self,match_query):
        """
        Return all lines that contain certain text inside of them.
        Supports fts4 query syntax.
        """
        query = '"{}"'.format(data_to_hex(match_query))
        return self.match_text_fts(query)

    def lines_text_tokens(self,match_query):
        """
        Return all lines that contain certain text tokens inside of them.
        Supports fts4 query syntax.
        """
        query = '"{}"'.format(match_query)
        return self.match_text_tokens_fts(query)

    def match_lines_data_hex(self,match_query):
        """
        Return all lines that contain certain data hex
        Supports fts4 query syntax
        """
        return self.match_data_fts(match_query)

    def lines_data(self,data):
        """
        Get all lines with certain data.
        """
        data_hex = data_to_hex(data)
        return self.match_data_fts('"{}"'.format(data_hex))

    def lines_in_range(self,start_address,end_address):
        """
        Get all lines in a given range of addresses, inclusive.
        """
        rows = self._conn.execute("""SELECT address,type,line_text_hex,
            line_data_hex FROM lines WHERE address >= ? AND address <= ?""",
            (start_address,end_address,))

        return self._iter_proxy(
            (Line(row[0],row[1],hex_to_data(row[2]),hex_to_data(row[3])) 
                for row in rows))

    def lines_above(self,line_address,dist):
        """
        Get amount lines above line (Including the line itself)
        """
        return self.lines_in_range(line_address, line_address + dist)


    def lines_below(self,line_address,dist):
        """
        Get amount lines below line (Including the line itself)
        """
        return self.lines_in_range(line_address - dist, line_address)

    def lines_around(self,line_address,dist):
        """
        Get amount lines below line (Including the line itself)
        """
        return self.lines_in_range(line_address - dist, 
                line_address + dist)

    
    def close(self):
        self._conn.close()
