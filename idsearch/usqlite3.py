"""
Updated sqlite3 module.
We can't use the sqlite3 module that comes together with python by default,
because it is outdated and does not support fts tables.
Therefore we have to download a newer sqlite3.dll and use it.

In order to use a newer sqlite3.dll we also need to copy _sqlite3.pyd from the
DLLs python dir.
"""

import sys
import os
import shutil
import urllib
import tempfile
import zipfile

from .exceptions import SetupError
from .module_loader import load_dynamic


SQLITE_ZIP_URL = "https://sqlite.org/2016/sqlite-dll-win32-x86-3150000.zip"

# Directory that this file sits in:
current_path = os.path.dirname(os.path.abspath(__file__))

# Directory of assets:
assets_dir = os.path.join(current_path,'assets')

def find_dlls_dir():
    """
    Find the directory equivalent to 'C:\python27\DLLs' at the current running
    python.
    """
    for pdir in sys.path:
        dll_path = os.path.join(pdir,'sqlite3.dll')
        pyd_path = os.path.join(pdir,'_sqlite3.pyd')
        if os.path.isfile(dll_path) and os.path.isfile(pyd_path):
            return pdir

    raise SetupError('DLLs dir was not found. Aborting.')


def copy_sqlite3_pyd():
    """
    Copy _sqlite3.pyd from python dlls dir into assets dir
    """
    python_dir = os.path.dirname(sys.executable)
    sqlite3_pyd_dest_path = os.path.join(assets_dir,'_sqlite3.pyd')
    # If the file already exists, we remove it:
    if os.path.isfile(sqlite3_pyd_dest_path):
        os.remove(sqlite3_pyd_dest_path)

    dlls_dir = find_dlls_dir()
    sqlite3_pyd_path = os.path.join(dlls_dir,'_sqlite3.pyd')
    shutil.copyfile(sqlite3_pyd_path,sqlite3_pyd_dest_path)

def download_sqlite3_dll():
    """
    Download sqlite3.dll from sqlite releases page, if it does not exist yet on
    the assets dir.
    """
    sqlite3_dll_path = os.path.join(assets_dir,'sqlite3.dll')
    if os.path.isfile(sqlite3_dll_path):
        # sqlite3.dll is already there. Nothing to do here.
        return

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir,'sqlite3.zip')
    urllib.urlretrieve(SQLITE_ZIP_URL,zip_path)
    extracted_dir = os.path.join(temp_dir,'extracted')
    os.makedirs(extracted_dir)
    zipfile.ZipFile(zip_path).extractall(extracted_dir)

    shutil.copyfile(os.path.join(extracted_dir,'sqlite3.dll'),
            sqlite3_dll_path)

    shutil.rmtree(temp_dir)

def is_fts4_supported(sqlite_module):
    """
    Check if fts4 is supported.
    """
    conn = sqlite_module.connect(':memory:')
    try:
        try:
            conn.execute("""CREATE VIRTUAL TABLE test_table USING fts4(
                    col_a, col_b)""")
        except sqlite_module.OperationalError:
            return False

        return True
    finally:
        conn.close()


def load_sqlite3():
    """
    Load an sqlite3 module that supports fts4, and return it.
    """
    # We don't try to download the dll on posix systems:
    if os.name == 'posix':
        import sqlite3 as _native_sqlite3
        return _native_sqlite3

    # Make sure that the assets_dir exists:
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    try:
        # Try to load first:
        my_sqlite3 = load_dynamic('_sqlite3',os.path.join(assets_dir,'_sqlite3.pyd'))
    except ImportError:
        copy_sqlite3_pyd()
        download_sqlite3_dll()
        my_sqlite3 = load_dynamic('_sqlite3',os.path.join(assets_dir,'_sqlite3.pyd'))

    if not is_fts4_supported(my_sqlite3):
        raise SetupError('Could not get sqlite3 with fts4 support!')


    return my_sqlite3

sqlite3 = load_sqlite3()
