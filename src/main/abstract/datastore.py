'''
Created on 17.09.2019

@author: pakala
'''


class DataStore(object):
    """
    The DataStore stores all data of raw and computed values.

    Data is addressed by channels.
    """

    def __init__(self):
        self.db = None  # TODO: create here a database object (SQLite)
        self.channels = {}

    def configure(self, configuration):
        """Configures data channels out of the given configuration.

        Data channels may be associated to IOAdapter values, or to
        computed values, thus return values of simple functions and
        aggregation functions.

        :param lxml.etree.ElementTree configuration: XML DOM tree of
        the configuration

        """
        pass

    def add_channel(self):
        pass

    def remove_channel(self):
        pass
