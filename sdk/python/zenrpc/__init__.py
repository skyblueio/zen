# Copyright 2018 Colin McGrath, or affiliates

import logging

from zenrpc.session import Session

__author__ = "Colin McGrath"
__version__ = '0.0.1'

# Global variable storing the default session. Ensures that when setting up
# the default session we do not get duplicates in the same runtime environment
DEFAULT_SESSION = None

def setup_default_session(**kwargs):
    """
    Set up the default session, passing through kwargs to the session
    __init__ constructor. This should not be called unless custom attributes
    are desired.
    """
    global DEFAULT_SESSION
    DEFAULT_SESSION = Session(**kwargs)

def set_stream_logger(name="zenrpc", level=logging.DEBUG, format_string=None):
    """
    Add a user-defined stream logger to for the given name and level to the
    logging module. By default, all zenrpc events are piped to ``stdout``.

       >>> import zenrpc
       >>> zenrpc.set_stream_logger('zenrpc', logging.INFO)

    :type name: string
    :param name: log group name
    :type level: int
    :param level: Logging level in default python logger
    :type format_string: string
    :param format_string: Log message format string (using % syntax)
    """
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def _get_default_session():
    """
    Get the default session from global, setup one if necessary.

    :return: The default session
    """
    if DEFAULT_SESSION is None:
        setup_default_session()
    
    return DEFAULT_SESSION

def client(*args, **kwargs):
    """
    Return a client object to interact with the zend process
    """
    return _get_default_session().client(*args, **kwargs)

# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger('zenrpc').addHandler(NullHandler())
