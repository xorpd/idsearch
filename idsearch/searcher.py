import os
from .search_db import SearchDB
from .exceptions import IDBUtilError, SearchDBError
from .func_iter import FuncIter

def load_sdb(sdb_path):
    """
    Load SearchDB for the current database.
    """
    if not os.path.isfile(sdb_path):
        raise IDBUtilError('sdb {} does not exist. You need to generate '
            'an index first!'.format(sdb_path))

    return SearchDB(sdb_path,FuncIter)



###########################################################################

def _addr_format_by_lines(lines):
    """
    Get address format that fits all lines.
    """
    max_address = max(lines,key=lambda line:line.address).address
    if max_address > 2**64:
        raise IDBUtilError('An address {} that is larger than 2**64! '
            'Aborting.'.format(max_address))
    if max_address > 2**32:
        return '0x{:016x}'
    elif max_address > 2**16:
        return '0x{:08x}'
    else:
        return '0x{:04x}'


def _pad_str(input_str,length):
    """
    Pad a string with trailing spaces to a total length.
    """
    if len(input_str) > length:
        return input_str[:length - 5] + ' ... '

    return input_str + ' ' * (length - len(input_str))


def print_lines(lines):
    """
    Print lines nicely.
    """
    lines = list(lines)
    if len(lines) == 0:
        return

    max_data_len = len(max(lines,key=lambda line:len(line.data)).data)
    max_data_len = min([max_data_len,10])
    # Find common address format:
    addr_format = _addr_format_by_lines(lines)
    for line in lines:
        line_str = addr_format.format(line.address) + ' : '
        line_data = line.data
        if line_data is None:
            line_data = ''
        line_str += _pad_str(line_data.encode('hex'),max_data_len * 2) + ' | '
        line_str += _pad_str(line.text,40)
        print(line_str)

