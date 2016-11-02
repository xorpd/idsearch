import idsearch
from idsearch.idb_util import gen_sdb as _gen_sdb, \
        gen_sdb_path as _gen_sdb_path
from idsearch.exceptions import IDBUtilError as _IDBUtilError
from idsearch.searcher import load_sdb as _load_sdb, print_lines
from idsearch.types import LineTypes, XrefTypes

# Generate sdb if non existent:
try:
    _gen_sdb()
except _IDBUtilError:
    pass

def load_this_sdb():
    """
    Load the idsearch index for this IDB.
    """
    idb_path = idaapi.cvar.database_idb
    sdb_path = _gen_sdb_path(idb_path)
    return _load_sdb(sdb_path)

