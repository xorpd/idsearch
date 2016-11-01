import logging
import os
import idc
from idsearch.idb_util import gen_sdb

logger = logging.getLogger('idsearch')


def gen_logfile_path(idb_path):
    # Change the last .idb to .sdb:
    return '.'.join(idb_path.split('.')[:-1] + ['logsdb'])

def run():

    # Get the path of the idb:
    idb_path = idaapi.cvar.database_idb

    # Set up logging:
    log_file_path = gen_logfile_path(idb_path)
    fh = logging.FileHandler(log_file_path)
    loglevel = logging.INFO
    fh.setLevel(loglevel)
    logger.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
        ' %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info('Run was called')

    try:
        logger.info('Calling index_idb')
        gen_sdb(sdb_path=None,overwrite=True)
        logger.info('Indexing completed successfully!')
    except:
        logger.exception('Unhandled exception inside run().')
    finally:
        idc.Exit(0)



if __name__ == '__main__':
    run()
