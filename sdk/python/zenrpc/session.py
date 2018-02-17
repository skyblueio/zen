"""
Contains the Session class for setting up a default zend session
"""

import sys
import ConfigParser

class Session(object):
    def __init__(self, config_file=None):
        """
        Construct a default session object to interact with zend.
        The configuration is grabbed from the zen.conf file. There
        is internal knowledge of known default locations of the
        zen.conf file, but if it is unknown, it may need to be
        specified at runtime.

        :type config: string
        :param config: The path to the zen.conf (or equivalent) file
        """
        self.config_file = config_file
        if self.config_file is None:
            self._query_config_file()

    def _query_config_file(self):
        """
        Search for the config file in defined default locations
        """
        
