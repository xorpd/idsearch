import logging
import idc
import idaapi
import idautils
from .gen_db import SDBGen
from .types import LineTypes, XrefTypes

logger = logging.getLogger(__name__)

def iter_lines():
    """
    Iterate through all line addresses in the IDB
    Yields addresses of all lines.
    """
    for ea in idautils.Segments():
        seg_start = idc.SegStart(ea)
        seg_end = idc.SegEnd(ea)

        cur_addr = seg_start
        while (cur_addr < seg_end) and (cur_addr != idaapi.BADADDR):
            yield cur_addr
            cur_addr = idc.NextHead(cur_addr)


def canonicalize_line_text(line_text):
    
    # Remove any non ascii characters:
    res_line_text = ""
    for c in line_text:
        if ord(c) >= 0x80:
            break
        res_line_text += c

    # Remove extra spaces:
    return unicode(' '.join(res_line_text.split()))


def is_func_chunked(func_addr):
    """
    Check if a function is divided into chunks.
    """
    logger.debug('is_func_chunked {}'.format(func_addr))
    # Idea for this code is from:
    # http://code.google.com/p/idapython/source/browse/trunk/python/idautils.py?r=344

    num_chunks = 0
    func_iter = idaapi.func_tail_iterator_t(idaapi.get_func(func_addr))
    status = func_iter.main()
    while status:
        chunk = func_iter.chunk()
        num_chunks += 1
        # yield (chunk.startEA, chunk.endEA)
        status = func_iter.next()

    return (num_chunks > 1)

def is_line_code(line_address):
    """
    Check if a given line contains code.
    """
    # Use a hack of trying to get the mnemonic:
    return idaapi.ua_mnem(line_address) is not None

def is_line_exists(line_address):
    """
    Check if a given address corresponds to a real line.
    """
    # Use a hack of trying to check if the line is code.
    # If we get an exception, this is probably not a real line:
    try:
        idaapi.isCode(line_address)
    except TypeError:
        return False
    return True



def index_idb(sdb_path):
    """
    Index the current idb.
    """
    sdbgen = SDBGen(sdb_path)

    sdbgen.begin_transaction()
    # Index all lines:
    for line_addr in iter_lines():
        # Get line attributes:
        line_type = LineTypes.DATA
        if is_line_code(line_addr):
            line_type = LineTypes.CODE

        line_text = canonicalize_line_text(idc.GetDisasm(line_addr))
        line_data = idc.GetManyBytes(line_addr,idc.ItemSize(line_addr))
        # Make sure that we don't insert Nones:
        if line_data is None:
            line_data = ""

        # Index the line:
        sdbgen.add_line(line_addr,line_type,line_text,line_data)


    sdbgen.commit_transaction()
            
    sdbgen.begin_transaction()
    # Index all xrefs:
    for line_addr in iter_lines():
        if is_line_code(line_addr):
            # Line is code:
            # Code xrefs:
            no_flow_crefs = set(idautils.CodeRefsFrom(line_addr,0))
            all_crefs = set(idautils.CodeRefsFrom(line_addr,1))
            flow_crefs = no_flow_crefs.difference(all_crefs)

            for nf_cref in no_flow_crefs:
                if not is_line_exists(nf_cref):
                    logger.warning('Code line: nf_cref = 0x{:x} is nonexistent. '
                        'line_addr = 0x{:x}'.format(nf_cref,line_addr))
                    continue 
                sdbgen.add_xref(XrefTypes.CODE_JUMP,line_addr,nf_cref)

            for f_cref in flow_crefs:
                if not is_line_exists(f_cref):
                    logger.warning('Code line: f_cref = 0x{:x} is nonexistent. '
                        'line_addr = 0x{:x}'.format(f_cref,line_addr))
                    continue
                sdbgen.add_xref(XrefTypes.CODE_FLOW,line_addr,f_cref)

            # Code to Data xrefs:
            for dref in idautils.DataRefsFrom(line_addr):
                if not is_line_exists(dref):
                    logger.warning('Code line: dref = 0x{:x} is nonexistent. '
                        'line_addr = 0x{:x}'.format(dref,line_addr))
                    continue
                sdbgen.add_xref(XrefTypes.CODE_TO_DATA,line_addr,dref)

        else:
            # Line is data (Not code):
            for dref in idautils.DataRefsFrom(line_addr):
                if not is_line_exists(dref):
                    logger.warning('Data line: dref = {:x} is nonexistent. '
                        'line_addr = 0x{:x}'.format(dref,line_addr))
                    continue

                if is_line_code(dref):
                    sdbgen.add_xref(XrefTypes.DATA_TO_CODE,line_addr,dref)
                else:
                    sdbgen.add_xref(XrefTypes.DATA_TO_DATA,line_addr,dref)

    sdbgen.commit_transaction()

    sdbgen.begin_transaction()
    # Index all functions:
    for func_addr in idautils.Functions():
        # We skip chunked functions:
        if is_func_chunked(func_addr):
            logger.warning('Function at 0x{:x} is chunked'.format(func_addr))
            continue

        func_end = idc.GetFunctionAttr(func_addr,idc.FUNCATTR_END)

        # Make sure that start is before end:
        if func_end <= func_addr:
            logger.warning('Function at {:x} has end {:x}'\
                    .format(func_addr,func_end))
            continue

        line_addresses = xrange(func_addr,func_end)
        func_name = idc.GetFunctionName(func_addr)
        sdbgen.add_function(func_addr,func_name,line_addresses)

    sdbgen.commit_transaction()


    sdbgen.fill_lines_fts()
    sdbgen.close()

