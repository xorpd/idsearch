from setuptools import setup

setup(name='idsearch',
    version='0.1',
    description='Fast searcher for the Interactive Disassembler',
    url='https://github.com/xorpd/idsearch',
    author='xorpd',
    author_email='xorpd@xorpd.net',
    license='GPLv3',
    packages=['idsearch'],
    zip_safe=False,
    include_package_data=True)

# include_package_data makes sure that MANIFEST.in files are considered.
# See: http://python-packaging.readthedocs.io/en/latest/non-code-files.html
