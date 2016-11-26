import os
import shutil

import unittest
from idsearch.types import LineTypes, XrefTypes
from idsearch.gen_db import SDBGen
from idsearch.types import data_to_hex, hex_to_data

class TestDBGen(unittest.TestCase):
    def test_basic_init(self):
        sdbgen = SDBGen(':memory:')
        sdbgen.close()

    def test_add_line(self):
        sdbgen = SDBGen(':memory:')
        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,
                'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
        sdbgen.close()

    def test_add_line_none_data(self):
        sdbgen = SDBGen(':memory:')
        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'db ?','')
        sdbgen.close()

    def test_add_line_transaction(self):
        sdbgen = SDBGen(':memory:')

        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,
                'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
        sdbgen.close()

    def test_fill_lines_fts(self):
        sdbgen = SDBGen(':memory:')

        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,
                'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
        sdbgen.fill_lines_fts()
        sdbgen.close()

    def test_add_xref(self):
        sdbgen = SDBGen(':memory:')

        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,
                'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
        sdbgen.add_xref(XrefTypes.CODE_FLOW,0x051fecb4,0x051fecb8)
        sdbgen.fill_lines_fts()
        sdbgen.close()

    def test_add_function(self):
        sdbgen = SDBGen(':memory:')

        sdbgen.add_line(0x051FECB4, LineTypes.CODE,'li r25,0','\x3B\x20\x00\x00')
        sdbgen.add_line(0x051FECB8, LineTypes.CODE,
                'addi r24, r1, 0x40+var_28','\x3B\x01\x00\x18')
        sdbgen.add_function(0x051fecb4,'my_func',[0x051fecb4,0x051fecb8])
        sdbgen.fill_lines_fts()
        sdbgen.close()


class TestDataToHex(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(data_to_hex('1234'),'31 32 33 34')
        self.assertEqual(data_to_hex(''),'')
        self.assertEqual(data_to_hex('aaa'),'61 61 61')

    def test_inverse(self):
        self.assertEqual(hex_to_data(data_to_hex('1234')),'1234')
        self.assertEqual(data_to_hex(hex_to_data('31 32 33')),'31 32 33')


