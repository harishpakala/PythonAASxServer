'''
Created on 17.09.2019

@author: pakala
'''

import abc



class AsssetEndPointHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, pyAAS, ip, port, username, password, propertylist):
        self.pyAAS = pyAAS
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password 
        self.propertylist = propertylist
        
    def add_raw_channel_ref(self, ref_id, address):
        self.raw_channel_refs[ref_id] = address

    def configure(self, ioAdaptor):
        """Configures the raw channels of the IOAdapter."""
        pass

    def read_channel(self, channel_id):
        """Returns a raw channel value."""
        channel = self.pyAAS.channels[channel_id]
        value = self.read(channel.io_address)
        return value

    def write_channel(self, channel_id, value):
        """Writes a value to a raw channel."""
        channel = self.pyAAS.channels[channel_id]
        self.write(channel.address, str(value))


    @abc.abstractmethod
    def read(self, address):
        """Returns a value according to the given address. This operation
        should use sophisticated caching strategies to achieve fast
        access to the requested values, e.g. query full blocks of data
        and only if a certain time is gone since last real query of
        data from the asset.

        """
        pass

    @abc.abstractmethod
    def write(self, address, value):
        """Writes a value to the given address. This operation should use
        sophisticated caching strategies to achieve fast access to the
        requested values, e.g. transmit full blocks of data and only
        if a certain time is gone since last real query of data from
        the asset.

        """
        pass
