# IDSearch

Search IDA databases like a boss.

## What is IDSearch?

IDSearch is a pythonic search tool for [IDA (Interactive
Disassembler)](https://www.hex-rays.com/index.shtml). It allows searching text
and data quickly in big databases. It also allows combination of various search
conditions using functional based syntax.

Requirements for your system:
- IDA >= 6.6
- Python >= 2.7
- Tested only on Windows >= 7. Might work on Linux, if your sqlite is new
  enough to support fts4. (On windows it is downloaded automatically if current
  version is too old).

## How it works?

IDSearch Works using python2.7 and [sqlite](https://sqlite.org/)
[fts4](https://www.sqlite.org/fts3.html) indexing.

IDSearch works in two steps: If first indexes your IDB (IDA database file) and
creates an optimized database called sdb (Search database). Any further queries
are performed against the optimized sdb.


## Basic Usage
### From inside IDA

Press Alt + F7, and run the file script file `ida_search.py`.
If this is the first time this is done for this IDB you will have to wait for
IDSearch to index it. This could take a few minutes. Be patient.

The index is kept as a file in the same path of your IDB file. It should have
the same name as the IDB, except for the extension: .sdb (Search Data Base).

When the indexing is done, you can start writing some code in IDA's python
shell. The first thing you will usually do is obtain a handle to the sdb using
the `load_this_sdb` function:

```python
Python>sdb = load_this_sdb()
```

This function opens a connection to the sdb database. It should return
immediately.


#### Find text tokens

Find the token 'Mozilla' inside the IDB:

```python
Python>print_lines(sdb.lines_text_tokens('Mozilla'))
0x0093984d : 488d1584082000 | lea rdx, aUserAgentMoz_0; "\r\nUser ... 
0x0094d579 : 488d1528f01e00 | lea rdx, aUserAgentMozil; "\r\nUser ... 
```

The results are obtained immediately.  
For comparison, the time of search using IDA's text search (Alt + T) is 46 seconds on my machine.

The text tokens search is very fast, hoever it does not allow to perform case
sensitive text searches, or exact text searches. For example, the text above
will not find Mozilla in a line that contains the string 'HiMozilla'. It will
find it inside the lines 'Hi,Mozilla' and 'Hi Mozilla'.

Note that `sdb.lines_text_tokens` is lazy. It returns a generator of line
objects:
```python
Python>sdb.lines_text_tokens('Mozilla')
<idsearch.func_iter.FuncIter object at 0x0597B4F0>
```

A line object contains some information about the found line:

```python
Python>lines = list(sdb.lines_text_tokens('Mozilla'))
Python>lines[0]
<idsearch.search_db.Line object at 0x0597B110>
Python>hex(lines[0].address)
0x93984d
Python>lines[0].text
lea rdx, aUserAgentMoz_0; "\r\nUser-Agent: Mozilla/4.0 (compatible"...
Python>lines[0].data.encode('hex')
488d1584082000
Python>lines[0].line_type == LineTypes.CODE
True
```

`print_lines` is a function that prints lines nicely from any iterator of lines.

#### Finding exact text

Finding exact text is a bit slower than text tokens search, but only a bit. It
is useful for finding exact text inside lines in your IDB. It it case
sensitive. Example:

```python
Python>print_lines(sdb.lines_text('User-Agent'))
0x0093984d : 488d1584082000 | lea rdx, aUserAgentMoz_0; "\r\nUser ... 
0x0094d51d : 488d155cf01e00 | lea rdx, aUserAgent ; "\r\nUser-Agent: "
0x0094d579 : 488d1528f01e00 | lea rdx, aUserAgentMozil; "\r\nUser ... 
```

and:

```python
Python>print_lines(sdb.lines_text('user-Agent'))
```

Note that this time no search results were found.

#### Finding exact data

Finding exact data is done using `sdb.lines_data` as follows:

```
Python>print_lines(sdb.lines_data('\x15\x33\x33'))
0x0047854e : 488d1533336800 | lea rdx, unk_AFB888  
```

#### Getting all items

Sometimes one might want to obtain all items of certain type. This is not very
efficient but sometimes necessary.

Getting all lines:
```python
lines = sdb.all_lines()
```

Getting all xrefs:
```python
xrefs = sdb.all_xrefs()
```

Getting all functions:
```python
functions = sdb.all_functions()
```

Note that all 




TODO

#### Xrefs

TODO

#### Function and Line translation

TODO

#### Lines around

TODO

#### Functional searches

TODO


### From outside IDA

You can index an IDB without opening IDA. This can be done using the
`standalone_index.py` script.

If my ida is installed at `c:\programs\ida`, idsearch is at
`c:\programs\idsearch` and the relevant IDB is at `c:\temp\my_project.idb`, you
can run the following command to index your IDB.

```
c:\programs\ida\idaq.exe -A -S"c:\programs\idsearch\standalone_index.py" "c:\temp\my_project.idb"
```

Note that this might take some time.

After you have indexed your IDB, assuming that you have idsearch installed for
your python environment (See installation instructions for info about this),
you can use the following code to do some searching:

```python
from idsearch.searcher import load_sdb
sdb = load_sdb(r'c:\temp\my_project.sdb')

# Find lines that contain the data 25 14 5A:
lines = sdb.lines_data('\x25\x14\x5A')

sdb.close()
```

## Installation

1.  git clone https://github.com/xorpd/idsearch

2.  (Optional step) for offline installation run:
    ```
    python prepare_offline_install.py
    ```
    Now you can take the directory with you for offline usage.

3.  (Optional step) If you want to install IDSearch as a python module.
    For example, using setuptools:
    ```
    python install_assets/ez_setup.py
    python setup.py install
    ```

    You can also use pip in one of the following ways:
    -   Editable mode:
        ```
        pip install -e .
        ```

    -   sdist:
        ```
        python setup.py sdist
        pip install dist\idsearch-?.?.tar
        ```

## Tests

IDSearch uses unittest for tests.
To run the test, use the command:

```
c:\projects\idsearch> python -m unittest discover 
```

If `c:\projects\idsearch` is where IDSearch is installed.


