import sys
import os
import shutil
import urllib
import tempfile
import zipfile

SQLITE_ZIP_URL = "https://sqlite.org/2016/sqlite-dll-win32-x86-3150000.zip"

# Directory that this file sits in:
current_path = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_path,'assets')


def copy_sqlite3_pyd():
    """
    Copy _sqlite3.pyd from python dlls dir into assets dir (If not there
    already).
    """
    python_dir = os.path.dirname(sys.executable)
    sqlite3_pyd_dest_path = os.path.join(assets_dir,'_sqlite3.pyd')
    if os.path.isfile(sqlite3_pyd_dest_path):
        # Already exists. We don't copy
        return

    sqlite3_pyd_path = os.path.join(python_dir,'DLLs','_sqlite3.pyd')
    shutil.copyfile(sqlite3_pyd_path,sqlite3_pyd_dest_path)

def download_sqlite3_dll():
    """
    Download sqlite3.dll from sqlite releases page, if it does not exist yet on
    the assets dir.
    """
    sqlite3_dll_path = os.path.join(assets_dir,'sqlite3.dll')
    if os.path.isfile(sqlite3_dll_path):
        # sqlite3.dll is already there. Nothing to do here.
        return

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir,'sqlite3.zip')
    urllib.urlretrieve(SQLITE_ZIP_URL,zip_path)
    extracted_dir = os.makedirs(temp_dir,'extracted')
    zipfile.ZipFile(zip_path).extractall(extracted_dir)

    shutil.copyfile(os.path.join(extracted_dir,'sqlite3.dll'),
            sqlite3_dll_path)

    shutil.rmtree(temp_dir)


if assets_dir not in sys.path:
    copy_sqlite3_pyd()
    download_sqlite3_dll()
    # Add the assets directory to path:
    sys.path.append(os.path.join(current_path,'assets'))


import sqlite3
