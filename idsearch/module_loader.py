import imp


def load_dynamic(name,pathname):
    """
    Load a dynamic module
    """
    # Python2 specific:
    return imp.load_dynamic(name,pathname)


