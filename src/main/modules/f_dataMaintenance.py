'''
Created on 07.11.2019

@author: pakala
'''
import random 

def createRandomData(propertyName):
    peak_chance = random.randint(0, 100)
    
    if peak_chance < 10:  # 10% chance for under-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2309, 2409) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6889, 6989) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    elif peak_chance > 90:  # 10% chance for peak-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2415, 2515) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(7045, 7145) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    else:
        if (propertyName == "Processvalue"):
            return float(random.randint(2409, 2415) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6989, 7045) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)

def function(pyAAS, *args):
    ''' Data Store Maintenance, for every 1 minutes this modules
        takes a copy of the assetDataTable, deletes from the 
        table values and moves the copy to  the cloud databasse
    '''
    pyAAS.dataStoreManager.assetDataStoreBackup()
