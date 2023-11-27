import logging
import logging.handlers
import os

def create_logger(filename):
    """Adds a handler to a new logger at the specified file location

    Takes in a filename/location and adds a logging handler to a new logger at the specified location with the specified name

    Keyword Arguements:
    filename -- string with the filename and location

    Return: Logger object with handler
    """
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'), mode='w')
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    handler.setFormatter(formatter)

    root = logging.getLogger(filename)
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.addHandler(handler)

    return root

def get_root_logger(filename):
    """Adds a handler to the root logger at the specified file location

    Takes in a filename/location and adds a logging handler to the root logger at the specified location with the specified name

    Keyword Arguements:
    filename -- string with the filename and location

    Return: Logger object with handler
    """
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'), mode='w')
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(os.environ.get('LOGLEVEL', 'INFO'))
    root.addHandler(handler)

    return root