
class LineTypes(object):
    CODE = 0
    DATA = 1

class XrefTypes(object):
    CODE_FLOW = 0
    CODE_JUMP = 1
    CODE_TO_DATA = 2
    DATA_TO_DATA = 3
    DATA_TO_CODE = 4

############################################################################

class Xref(object):
    def __init__(self,xref_type,line_from,line_to):
        self.xref_type = xref_type
        self.line_from = line_from
        self.line_to = line_to

class Line(object):
    def __init__(self,address,line_type,text,data):
        self.address = address
        self.line_type = line_type
        self.text = text
        self.data = data

class Function(object):
    def __init__(self,address,name):
        self.address = address
        self.name = name

###########################################################################


def data_to_hex(data):
    """
    Convert data to space separated hex bytes.
    """
    return " ".join(map(lambda c:c.encode('hex').lower(),data))

def hex_to_data(data_hex):
    """
    Convert space separated hex bytes to data.
    """
    return ''.join(
        map(lambda chex:chex.decode('hex'),data_hex.split(' '))
    )
