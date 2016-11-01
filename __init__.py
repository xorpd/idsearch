from idsearch import idb_util
from idsearch import searcher

from idsearch.searcher import *
from idsearch.types import *

sdb_path= idb_util.gen_sdb_path(idaapi.cvar.database_idb)
sdb = searcher.load_sdb(sdb_path)
