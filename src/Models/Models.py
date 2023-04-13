import csv
import os

modelsDirectory = os.path.dirname(__file__)
resourcesDirectory = os.path.join(modelsDirectory, '../../Resources')
edsFolder = 'C:/EDS PLOTS'
pathToEDSFile = os.path.join(edsFolder, '%T.MAIN')

class Model():
    def __init__(self):
       self.__indexes = []

    def generateCurveFiles(self, eng):
        #Return false if no engineer is selected
        if self.__engineerExists(eng) == False:
            errorMessage = "Please selected an Engineer!"
            return [False, errorMessage]
        
        totalLines = self.__readDesign()

        curve1LineNumbers = []
        curve2LineNumbers = []
        curve3LineNumbers = []

        if totalLines >= 400:      #All three curves will be included
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
            curve2LineNumbers = [self.__indexes[2], self.__indexes[3]]
            curve3LineNumbers = [self.__indexes[4], self.__indexes[5]]

        elif totalLines > 325 and totalLines < 375:     
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
            curve2LineNumbers = [self.__indexes[2], self.__indexes[3]]
        
        elif totalLines < 300:
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
        
        self.__extractCurves(curve1LineNumbers)
        self.__extractCurves(curve2LineNumbers)
        self.__extractCurves(curve3LineNumbers)
                
        successMessage = "Curves have been imported!"
        return [True, successMessage]
    
    def __engineerExists(self, eng):
        if eng in ['GM','PMV','DM','PR','DW']:
            return True
        else:
            return False
        
    def __readDesign(self):
        self.__fileName = os.path.join(pathToEDSFile)
        self.__file = open(self.__fileName)
        self.__fileContent = self.__file.read().split('\n')
        index = 0
        for line in self.__fileContent:
            if line != "":
                if line[1:3] == '1.' or line[0:8] == 'Pull-out':
                    self.__indexes.append(index)

            index = index + 1
        return len(self.__fileContent)
    
    def __extractCurves(self, lineNumbers):

        if len(lineNumbers) == 0:
            return

        for linenumber in range(lineNumbers[0], lineNumbers[1]):
            line = self.__fileContent[linenumber]
            speed = line[:8]
            torque = line[9:15]
            current = line[16:22]
            load = line[38:44]
            print(speed + " " + torque + " " + current + " " + load)