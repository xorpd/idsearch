
class LineTypes(object):
    CODE = 0
    DATA = 1

class XrefTypes(object):
    CODE_FLOW = 0
    CODE_JUMP = 1
    CODE_TO_DATA = 2
    DATA_TO_DATA = 3
    DATA_TO_CODE = 4


def data_to_hex(data):
    """
    Convert data to space separated hex bytes.
    """
    if data is None:
        return None

    return " ".join(map(lambda c:c.encode('hex').lower(),data))

def hex_to_data(data_hex):
    """
    Convert space separated hex bytes to data.
    """
    if data_hex is None:
        return None

    return ''.join(
        map(lambda chex:chex.decode('hex'),data_hex.split(' '))
    )
