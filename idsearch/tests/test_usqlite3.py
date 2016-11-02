import unittest
from idsearch.usqlite3 import sqlite3

class TestSearchDB(unittest.TestCase):
    def test_example_fts4(self):
        conn = sqlite3.connect(':memory:')
        conn.execute("""CREATE VIRTUAL TABLE test_table USING fts4(
                col_a, col_b)""")
        conn.close()
