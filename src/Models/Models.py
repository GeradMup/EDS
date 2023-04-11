import csv
import os

pathToEDSFile = 'C:/Users/gerry/Documents/Work/ACTOM/EDS/Resources/%T.MAIN'
class Model():
    def __init__(self):
       pass

    def generateCurveFiles(self, eng):
        #Return false if no engineer is selected
        if eng == "":
            errorMessage = "Please selected an Engineer!"
            return [False, errorMessage]
        
        self.__fileName = os.path.join(pathToEDSFile)
        self.__file = open(self.__fileName)
        self.__fileContent = self.__file.read().split('\n')
    
        for line in self.__fileContent:
            print(line)
        
        successMessage = "Curves have been imported!"
        return [True, successMessage]