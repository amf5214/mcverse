import logging
import logging.handlers
import os
import configparser

def create_logger(filename):
    """Adds a handler to a new logger at the specified file location

    Takes in a filename/location and adds a logging handler to a new logger at the specified location with the specified name

    Keyword Arguements:
    filename -- string with the filename and location

    Return: Logger object with handler
    """
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'), mode='a')
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
    handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", f'logging/{filename}.log'), mode='a')
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(os.environ.get('LOGLEVEL', 'INFO'))
    root.addHandler(handler)

    return root

def log_message(message, main=False, level='info'):
    logging_active = False
    app_config_file = 'appconfig.ini'
    if os.path.isfile(app_config_file):
        config = configparser.ConfigParser()
        config.read(app_config_file)
        logging_active = True if config['Main']['logging'] == "True" else False

    logger = None

    if logging_active and not main:
        logger = create_logger('internal_operations')

    elif logging_active and main:
        logger = get_root_logger('root')

    if logger != None and logging_active:
        if level == 'error':
            logger.error(message)
        elif level == 'info':
            logger.info(message)