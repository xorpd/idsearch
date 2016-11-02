import sys

def run():
    print('Collecting assets...')
    from idsearch.usqlite3 import sqlite3, is_fts4_supported
    print('Testing operation of sqlite3...')
    if is_fts4_supported(sqlite3):
        print('Success!')
        return 0
    else:
        print('Failure!')
        return 1


if __name__ == '__main__':
    sys.exit(run())
