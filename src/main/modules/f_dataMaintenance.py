'''
Created on 07.11.2019

@author: pakala
'''


def function(pyAAS, *args):
    ''' Data Store Maintenance, for every 1 minutes this modules
        takes a copy of the assetDataTable, deletes from the 
        table values and moves the copy to  the cloud databasse
    '''
    pyAAS.dataStoreManager.assetDataStoreBackup()
