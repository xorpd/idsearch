import sys
import os
import urllib

from idsearch.obtain_assets import download_sqlite3_dll

EZ_SETUP_URL = "https://bootstrap.pypa.io/ez_setup.py"

# Path of current directory:
current_path = os.path.dirname(os.path.abspath(__file__))

def run():
    print('Collecting assets...')

    # Make sure that install_assets directory exists:
    install_assets_dir = os.path.join(current_path,'install_assets')
    if not os.path.exists(install_assets_dir):
        os.makedirs(install_assets_dir)
    # ez_setup.py, for setuptools. This could be useful for later installation
    # of the packages using python setup.py install

    ez_setup_path = os.path.join(install_assets_dir,'ez_setup.py')
    if not os.path.isfile(ez_setup_path):
        # Download if non existent:
        urllib.urlretrieve(EZ_SETUP_URL,ez_setup_path)

    # Download sqlite3.dll:
    download_sqlite3_dll()

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
