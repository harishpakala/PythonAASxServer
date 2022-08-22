'''
Created on 17.09.2019

@author: pakala
'''
from datetime import datetime
import uuid


class Channel(object):
    """The channel representation."""

    def __init__(self, saas):
        self.saas = saas
        self.io_adapter = None  # is redefined in case of raw channels
        self.io_address = None
        self.current_value = None
        # self.save(current_value)
        # self.get_time_series(start_inclusive, end_inclusive)

    def configure(self, channel):
        self.id = channel["propertyName"]
        self.name = channel["propertyName"]
        self.type = "float"
        
#         if "TimeSeries" in xelement.attrib:
#             self.is_timeseries = xelement.attrib["TimeSeries"]
#         else:
#             self.is_timeseries = False
#         if "Description" in xelement.attrib:
#             self.description = xelement.attrib["Description"]
#         else:
#             self.description = ""

    def set_io_adapter(self, io_adapter):
        self.io_adapter = io_adapter

    def read(self):
        if self.io_adapter is None:
            return self.current_value
            # TODO: think about to retrieve last value of the database channel
        else:
            adapter = self.saas.io_adapters[self.io_adapter]
            return adapter.read_channel(self.id)

    def write(self, value):
        self.current_value = value
        if self.io_adapter is None:
            # TODO: think about to put the value into the database channel
            pass
        else:
            self.io_adapter.write_channel(self.id, value)

    def update(self):
        
        newvalueDict = {}
        newvalueDict['name'] = self.name
        newvalueDict['channel_id'] = self.id
        newvalueDict['value'] = self.read()
        newvalueDict['datetimestamp'] = str(datetime.now())
        newvalueDict['id'] = uuid.uuid4()
        self.saas.msgHandler.putAssetMessage(newvalueDict)
