"""
Updated sqlite3 module.
We can't use the sqlite3 module that comes together with python by default,
because it is outdated and does not support fts tables.
Therefore we have to download a newer sqlite3.dll and use it.

In order to use a newer sqlite3.dll we also need to copy _sqlite3.pyd from the
DLLs python dir.
"""
import os

from .exceptions import SetupError
from .module_loader import load_dynamic
from .obtain_assets import copy_sqlite3_pyd, download_sqlite3_dll

# Directory that this file sits in:
current_path = os.path.dirname(os.path.abspath(__file__))

# Directory of assets:
assets_dir = os.path.join(current_path,'assets')

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
