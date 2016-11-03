import unittest

import os
import shutil
import tempfile

from idsearch.gen_db import SDBGen
from idsearch.search_db import SearchDB
from idsearch.types import LineTypes, XrefTypes
from idsearch.types import hex_to_data, data_to_hex

def fill_sdb(sdb_path):
    """
    Fill the database with some example rows.
    """
    sdbgen = SDBGen(sdb_path)
    sdbgen.begin_transaction()
    sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
    sdbgen.add_line(0x051FECB8, LineTypes.CODE,
            'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
    sdbgen.add_line(0x051FECBC, LineTypes.CODE, 'bctrl','\x4e\x80\x04\x21')
    sdbgen.add_line(0x051FECC0, LineTypes.CODE, 'li r4,-1','\x38\x80\xff\xff')
    sdbgen.add_line(0x051FECC4, LineTypes.CODE, 'li r5,-1','\x38\xA0\xff\xff')
    sdbgen.add_line(0xFF000000, LineTypes.CODE, 'empty','')

    sdbgen.add_xref(XrefTypes.CODE_FLOW,0x051fecb4,0x051fecb8)
    sdbgen.add_function(0x051fecb4,'my_func',[0x051fecb4,0x051fecb8])
    sdbgen.commit_transaction()
    sdbgen.fill_lines_fts()
    sdbgen.close()


class TestSearchDB(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory:
        self.my_dir = tempfile.mkdtemp()
        my_sdb_path = os.path.join(self.my_dir,'mydb.sdb')
        fill_sdb(my_sdb_path)

        self.sdb = SearchDB(my_sdb_path)

    def tearDown(self):
        self.sdb.close()
        # Remote temporary directory:
        shutil.rmtree(self.my_dir)

    def test_get_all(self):
        functions = list(self.sdb.all_functions())
        self.assertEqual(len(functions),1)

        lines = list(self.sdb.all_lines())
        self.assertEqual(len(lines),6)

        xrefs = list(self.sdb.all_xrefs())
        self.assertEqual(len(xrefs),1)


    def test_get_line(self):

        line = self.sdb.get_line(0x051fecb4)
        self.assertEquals(line.address,0x051fecb4)
        self.assertEquals(line.data,'\x3b\x20\x00\x00')
        self.assertEquals(line.line_type,LineTypes.CODE)
        self.assertEquals(line.text,'li r25,0')


    def test_xrefs_from(self):

        xrefs = list(self.sdb.xrefs_from(0x051fecb4))
        self.assertEqual(len(xrefs),1)
        xref = xrefs[0]

        self.assertEqual(xref.line_from,0x051fecb4)
        self.assertEqual(xref.line_to,0x051fecb8)
        self.assertEqual(xref.xref_type,XrefTypes.CODE_FLOW)


    def test_xrefs_to(self):

        xrefs = list(self.sdb.xrefs_to(0x051fecb8))
        self.assertEqual(len(xrefs),1)
        xref = xrefs[0]

        self.assertEqual(xref.line_from,0x051fecb4)
        self.assertEqual(xref.line_to,0x051fecb8)
        self.assertEqual(xref.xref_type,XrefTypes.CODE_FLOW)

    def test_lines_in_func(self):

        lines = list(self.sdb.lines_in_func(0x051fecb4))
        self.assertEqual(len(lines), 2)
        slines = sorted(lines,key=lambda l:l.address)
        self.assertEqual(slines[0].address,0x051fecb4)
        self.assertEqual(slines[1].address,0x051fecb8)


    def test_funcs_by_line(self):
        funcs = list(self.sdb.funcs_by_line(0x051fecb8))
        self.assertEqual(len(funcs), 1)
        func = funcs[0]
        self.assertEqual(func.address,0x051fecb4)


    def test_lines_text(self):
        lines = list(self.sdb.lines_text('li'))
        self.assertEqual(len(lines),3)

        lines = list(self.sdb.lines_text('li r25'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('li r26'))
        self.assertEqual(len(lines),0)

        lines = list(self.sdb.lines_text('bctrl'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('0x40'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('0x4'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('var_28'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('0x40 var_28'))
        self.assertEqual(len(lines),0)

        lines = list(self.sdb.lines_text('var'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('28'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_text('bctrll'))
        self.assertEqual(len(lines),0)

        lines = list(self.sdb.lines_text('bct'))
        self.assertEqual(len(lines),1)

    def test_lines_text_tokens(self):
        lines = list(self.sdb.lines_text_tokens('li'))
        self.assertEqual(len(lines),3)

        lines = list(self.sdb.lines_text_tokens('bctrl'))
        self.assertEqual(len(lines),1)


    def test_match_lines_data_hex(self):

        lines = list(self.sdb.match_lines_data_hex('4E'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.match_lines_data_hex('"4E 80"'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.match_lines_data_hex('"38 A0"'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.match_lines_data_hex('"38 A1"'))
        self.assertEqual(len(lines),0)


    def test_lines_data(self):
        lines = list(self.sdb.lines_data('\x80\x04'))
        self.assertEqual(len(lines),1)

        lines = list(self.sdb.lines_data('\x38'))
        self.assertEqual(len(lines),2)

    def test_lines_in_range(self):
        self.assertEqual(
            len(list(self.sdb.lines_in_range(0x051fecbc,0x051fecc0))),2)
        self.assertEqual(
            len(list(self.sdb.lines_in_range(0x051fecbc,0x051fecbc))),1)

        self.assertEqual(
            len(list(self.sdb.lines_in_range(0x051fecbe,0x051fecbc))),0)

    def test_lines_around(self):
        self.assertEqual(
            len(list(self.sdb.lines_around(0x051fecbc,4))),3)
        self.assertEqual(
            len(list(self.sdb.lines_above(0x051fecbc,4))),2)
        self.assertEqual(
            len(list(self.sdb.lines_below(0x051fecbc,4))),2)


class TestSearchFTS(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory:
        self.my_dir = tempfile.mkdtemp()
        my_sdb_path = os.path.join(self.my_dir,'mydb.sdb')

        # Fill in sdb:
        sdbgen = SDBGen(my_sdb_path)
        sdbgen.begin_transaction()
        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'Hello there','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,'I am a line','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECBC, LineTypes.CODE,'I am another line','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECC0, LineTypes.CODE,'I am the next line','\x3B\x20\x00\x00')
        sdbgen.commit_transaction()
        sdbgen.fill_lines_fts()
        sdbgen.close()

        self.sdb = SearchDB(my_sdb_path)

    def tearDown(self):
        self.sdb.close()
        # Remote temporary directory:
        shutil.rmtree(self.my_dir)

    def test_and(self):
        pass


