import logging
import logging.handlers
import os

def create_logger(filename):
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'))
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger(filename)
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.addHandler(handler)

    return root

def get_root_logger(filename):
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'))
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.addHandler(handler)

    return root