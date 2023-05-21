"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from importlib import import_module
import threading

try:
    from modules import *
except ImportError:
    from src.main.modules import *


class Scheduler:
    """
    The scheduler of the Administration Shell
    """

    def __init__(self, pyaas):
        self.pyaas = pyaas
        self.jobs = dict()

    def configure(self) -> bool:
        """
        Configures the PyAAS Scheduler
        return True / False
        """
        try:
            for _uuid in self.pyaas.aasShellHashDict._getKeys():
                _shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
                if (_shellObject.asset_interface_description != None):
                    for property_name,_property in _shellObject.asset_interface_description.properties.items():
                        if _property.update_frequency == "subscribe":
                            update_function = import_module("modules." + "f_property_subscribe").function
                            self.jobs[property_name] = threading.Thread(target=update_function, args=(_property,))
                        elif str(_property.update_frequency) != "0":
                            update_function = import_module("modules." + "f_property_read").function
                            self.jobs[property_name] = threading.Thread(target=update_function, args=(_property,self.pyaas.asset_access_handlers,))
        except SystemError as e:
            self.pyaas.servself.serviceLogger.info(
                "Error configuring PyAAS Scheduler " + str(e)
            )
        return False

    def start(self) -> bool:
        """Runs the scheduler.

            return True or False

        """
        try:
            for job_name in self.jobs.keys():
                self.jobs[job_name].start()
        except SystemError as e:
            self.pyaas.servself.serviceLogger.info(
                "Error starting PyAAS Scheduler " + str(e)
            )
        return False

    def stop(self) -> bool:
        try:
            print("Scheduler stopped")
            # self.scheduler.shutdown()
            return True
        except SystemError as e:
            self.pyaas.servself.serviceLogger.info(
                "Error stopping PyAAS Scheduler " + str(e)
            )
        return False
    
    def update_scheduler(self,aid_property) -> bool:
        try:
            if aid_property.update_frequency == "subscribe":
                update_function = import_module("modules." + "f_property_subscribe").function
                th = threading.Thread(target=update_function, args=(aid_property,))
                th.start()
            elif str(aid_property.update_frequency) != "0":
                update_function = import_module("modules." + "f_property_read").function
                th = threading.Thread(target=update_function, args=(aid_property,self.pyaas.asset_access_handlers,))
                th.start()
            return True
        except SystemError as e:
            print(str(e))
        return False 
    