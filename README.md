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

## How does it work?

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

#### Lines

Lines are the most basic component of the indexing mechanism. A line
corresponds to one line in your IDB. It contains the attributes:

-   `address`: The address of the line. No two lines has the same address.

-   `line_type`: Code or Data.

-   `text`: The text that can be seen on the line (Not including the address
      and the bytes).

-   `data`: The data bytes that corresponds to the line in IDA. 
    Some lines do not contain any data (For example, lines in an uninitialized
    data section). In this case `data` will be an empty string.

One can use the `sdb.get_line` method to obtain a line object given a line
address. As an example, consider this line from IDA:

```
.text:00000000009399F9      mov     rdx, [rbp+var_8]
```

This is how we examine the line inside IDSearch:

```python
Python>line = sdb.get_line(0x9399f9)
Python>hex(line.address)
0x9399f9
Python>line.line_type == LineTypes.CODE
True
Python>line.text
mov rdx, [rbp+var_8]
Python>line.data.encode('hex')
488b55f8
```


#### Find lines with text tokens

Find the token 'Mozilla' inside the IDB:

```python
Python>print_lines(sdb.lines_text_tokens('Mozilla'))
0x0093984d : 488d1584082000 | lea rdx, aUserAgentMoz_0; "\r\nUser ... 
0x0094d579 : 488d1528f01e00 | lea rdx, aUserAgentMozil; "\r\nUser ... 
```

`print_lines` is a function that prints lines nicely from any iterator of lines.

The results are obtained immediately.  
For comparison, the time of search using IDA's text search (Alt + T) is 46 seconds on my machine.

The text tokens search is very fast, hoever it does not allow to perform case
sensitive text searches, or exact text searches. For example, the text above
will not find Mozilla in a line that contains the string 'HiMozilla'. It will
find it inside the lines 'Hi,Mozilla' and 'Hi Mozilla'.

Note that `sdb.lines_text_tokens` is lazy. It returns a iterator of line
objects:
```python
Python>sdb.lines_text_tokens('Mozilla')
<idsearch.func_iter.FuncIter object at 0x0597B4F0>
```


#### Find lines with exact text

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

#### Find lines with exact data

Finding exact data is done using `sdb.lines_data` as follows:

```
Python>print_lines(sdb.lines_data('\x15\x33\x33'))
0x0047854e : 488d1533336800 | lea rdx, unk_AFB888  
```

#### Line ranges

It is possible to filter lines based on their addresses.
The relevant methods are: 

- `sdb.lines_in_range(start_address, end_address)`: Find all lines with address
  in the given range.

- `sdb.lines_above(line_address_dist)`: Find all the lines with address in
  range `line_address` to `line_address + dist`, inclusive.

- `sdb.lines_below(line_address_dist)`: Find all the lines with address in
  range `line_address - dist` to `line_address`, inclusive.

- `sdb.lines_around(line_address_dist)`: Find all the lines with address in
  range `line_address - dist` to `line_address + dist`, inclusive.

Example:

```python
Python>print_lines(sdb.lines_around(0x9399f9,0x16))
0x009399e3 : e88837b6ff           | call sub_49D170                         
0x009399e8 : 488b8da0ebffff       | mov rcx, [rbp+var_1460]                 
0x009399ef : 488b056add2500       | mov rax, cs:qword_B97760                
0x009399f6 : 48ffd0               | call rax ; qword_B97760                 
0x009399f9 : 488b55f8             | mov rdx, [rbp+var_8]                    
0x009399fd : 488d4de0             | lea rcx, [rbp+var_20]                   
0x00939a01 : 49b80400000000000000 | mov r8, 4                               
0x00939a0b : e880afacff           | call sub_404990           
```
        

#### Xrefs

Xrefs are connections between lines. The supported xref types are (Taken from
types.py):

```python
class XrefTypes(object):
    CODE_FLOW = 0
    CODE_JUMP = 1
    CODE_TO_DATA = 2
    DATA_TO_DATA = 3
    DATA_TO_CODE = 4
```

The method `sdb.xrefs_to` allows to find all xrefs to a given line address.

```python
Python>xrefs = list(sdb.xrefs_to(0x9399f9))
Python>xrefs
[<idsearch.search_db.Xref object at 0x04C5B210>, <idsearch.search_db.Xref object at 0x04C5B490>]
Python>hex(xrefs[0].line_from)
0x939592
Python>hex(xrefs[0].line_to)
0x9399f9
```

The method `sdb.xrefs_from` works similarly, and allows to find all xrefs from
a given line address to other lines.


#### Function and Line translation

Every function contains some lines, and every line is possibly inside a few
functions (This relation was chosen to allow possible future support for
function chunks).

It is possible to translate between functions and lines using the methods:

- `sdb.lines_in_func(func_addr)`: Returns an iterator of all the lines inside a
  function.

- `sdb.funcs_by_line(line_address)`: Returns an iterator of all functions that
  contain the given line. Usually it will be just one function.

Example for printing all the lines in a function given some line in the middle
of the function:

```python
Python>func = list(sdb.funcs_by_line(0x939a0b))[0]
Python>print_lines(sdb.lines_in_func(func.address))
0x00939210 : 55                   | push rbp                                
0x00939211 : 4889e5               | mov rbp, rsp                            
0x00939214 : 4881eca0180000       | sub rsp, 18A0h                          
0x0093921b : 898424a4080000       | mov [rsp+18A0h+var_FFC], eax            
0x00939222 : 890424               | mov [rsp+18A0h+var_18A0], eax           
...
0x00939c4a : 0fb645e8             | movzx eax, [rbp+var_18]                 
0x00939c4e : c9                   | leave                                   
0x00939c4f : c3                   | retn                                    
```

Above, func is a Function object. It contains the attributes address and name:
```
Python>hex(func.address)
0x939210
Python>func.name
sub_939210
```


#### Getting all lines, xrefs, functions

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

Note that all the resulting lines, xrefs and functions are iterators. They are
lazily evaluated.

Example for counting the amount of lines in the index:

```python
Python>sum(1 for _ in sdb.all_lines())
1398021
```

#### Functional searches

The iterators being returned from calls to `sdb`'s methods are "improved".
They were given a few extra methods to allow combining search conditions in a
functional manner.

As an example, assume that you want to find all the lines with the immediate
100h that have the 'rdx' register mentioned, and that have address with
remainder 2 modulo 9. You can run the following query:

```python
Python>print_lines(sdb.lines_text_tokens('100h').filter(lambda l:('rdx' in l.text) and (l.address % 9) == 2))
0x0041baf3 : 48ba0001000000000000 | mov rdx, 100h                           
0x004a7be1 : 488d9500ffffff       | lea rdx, [rbp-100h]                     
0x005a607a : ff9200010000         | call qword ptr [rdx+100h]               
0x006e6b0a : 488b8a00010000       | mov rcx, [rdx+100h]                     
0x0076815b : 488b9000010000       | mov rdx, [rax+100h]                     
0x0078821c : 48898200010000       | mov [rdx+100h], rax                     
0x00788369 : 48898200010000       | mov [rdx+100h], rax                     
0x007883d5 : 48898200010000       | mov [rdx+100h], rax                     
0x0078d619 : 488d9500ffffff       | lea rdx, [rbp-100h]                     
0x007a76e9 : 488d9000010000       | lea rdx, [rax+100h]                     
0x007b2fa8 : 8a941000010000       | mov dl, [rax+rdx+100h]                  
0x00933968 : 4c8b8200010000       | mov r8, [rdx+100h]                      
0x00950f84 : 488b9300010000       | mov rdx, [rbx+100h]       
```

Note that the inner expression (Without the `print_lines` call) is an iterator.
It is evaluated lazily: This means that it is only calculated at the point when
we want to print it:

```python
sdb.lines_text_tokens('100h').filter(lambda l:('rdx' in l.text) and (l.address % 9) == 2)
<idsearch.func_iter.FuncIter object at 0x05A2BA90>
```

The additional methods that are supplied to each iterator returned from the sdb
methods are:

-   `map(func)`: Creates a new iterator where every original element x is mapped
    to func(x).

-   `filter(func)`: Creates a new iterator where an element x shows up only if
    func(x) == True. Otherwise it is discarded.

-   `unique(key)`: Creates a new iterator where an element x shows up only if
    key(x) does not equal to key(y) for some earlier element y.

-   `all(func)`: Returns True if func(x) is True for all elements x. Returns
    False otherwise.

-   `any(func)`: Returns True if func(x) is True for any element x. Returns
    False otherwise.


Example: Find all the lines that contain 'call rax' and have 'rcx' mentioned on
the line above them:

```python
Python>print_lines(sdb.lines_text('call rax').filter(lambda l:sdb.lines_above(l.address,0x4).any(lambda l:'rcx' in l.text)))
0x004aef78 : 48ffd0 | call rax                                
0x004af0f2 : 48ffd0 | call rax                                
0x0063e275 : 48ffd0 | call rax                                
0x007acb4a : 48ffd0 | call rax                                
0x007bfc40 : 48ffd0 | call rax                                
0x0094f0fa : 48ffd0 | call rax                                
```


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
    python install_assets\ez_setup.py
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

## Known limitations

- IDSearch does not deal with chunked functions.

