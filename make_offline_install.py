import sys
import urllib

EZ_SETUP_URL = https://bootstrap.pypa.io/ez_setup.py

# Path of current directory:
current_path = os.path.dirname(os.path.abspath(__file__))

def run():
    print('Collecting assets...')
    # ez_setup.py, for setuptools. This could be useful for later installation
    # of the packages using python setup.py install
    ez_setup_path = os.path.join(current_path,'install_assets','ez_setup.py')
    urllib.urlretrieve(EZ_SETUP_URL,ez_setup_path)

    # This should automatically download sqlite3.dll:
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
