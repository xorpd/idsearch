import os

from .exceptions import IDBUtilError
from .idb_indexer import index_idb

import idaapi


def gen_sdb_path(idb_path):
    """
    If idb is c:\temp\my_proj.idb, the sdb will be c:\temp\my_proj.sdb
    """
    # Change the last .idb to .sdb:
    return '.'.join(idb_path.split('.')[:-1] + ['sdb'])


def gen_sdb(sdb_path=None,overwrite=False):
    """
    Generate SearchDB for the current database (Slow!)
    """
    if sdb_path is None:
        # Get the path of the idb:
        idb_path = idaapi.cvar.database_idb
        sdb_path = gen_sdb_path(idb_path)

    if os.path.isfile(sdb_path):
        if not overwrite:
            raise IDBUtilError('sdb {} already exists. Use overwrite=True if '
                    'you want to overwrite.'.format(sdb_path))
        os.remove(sdb_path)

    # Index current IDB:
    index_idb(sdb_path)

