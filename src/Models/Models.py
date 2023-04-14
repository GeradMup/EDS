import csv
import os
from dataclasses import dataclass

modelsDirectory = os.path.dirname(__file__)
resourcesDirectory = os.path.join(modelsDirectory, '../../Resources')
edsFolder = 'C:/EDS PLOTS'
pathToEDSFile = os.path.join(resourcesDirectory, '%T.MAIN')

#----------------------------------------------------------------------------------------------------------------------
@dataclass
class Curves():
    speed = []
    torque = []
    current = []
    load = []

#----------------------------------------------------------------------------------------------------------------------
class Model():
    def __init__(self):
       self.__indexes = []
       self.__curves = []

    #----------------------------------------------------------------------------------------------------------------------
    def generateCurveFiles(self, eng):
        #Return false if no engineer is selected
        if self.__engineerExists(eng) == False:
            errorMessage = "Please selected an Engineer!"
            return [False, errorMessage]
        
        self.__readDesign()

        curve1LineNumbers = []
        curve2LineNumbers = []
        curve3LineNumbers = []

        if len(self.__indexes) == 6:        #All three voltage points avaiable: 100%, first percentage and second percentage
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
            curve2LineNumbers = [self.__indexes[2], self.__indexes[3]]
            curve3LineNumbers = [self.__indexes[4], self.__indexes[5]]

        elif len(self.__indexes) == 4:      #Only two voltage points available. 100% and first percentage     
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
            curve2LineNumbers = [self.__indexes[2], self.__indexes[3]]
        
        elif len(self.__indexes) == 2:      #Only the 100% Voltage point is available
            curve1LineNumbers = [self.__indexes[0], self.__indexes[1]]
        
        self.__extractCurves(curve1LineNumbers)
        self.__extractCurves(curve2LineNumbers)
        self.__extractCurves(curve3LineNumbers)
        
        self.__generateCsvFiles(eng)

        successMessage = "Curves have been imported!"
        return [True, successMessage]
    
    #----------------------------------------------------------------------------------------------------------------------
    def __engineerExists(self, eng):
        if eng in ['GM','PMV','DM','PR','DW']:
            return True
        else:
            return False

    #----------------------------------------------------------------------------------------------------------------------    
    def __readDesign(self):
        self.__fileName = os.path.join(pathToEDSFile)
        self.__file = open(self.__fileName)
        self.__fileContent = self.__file.read().split('\n')
        index = 0
        for line in self.__fileContent:
            if line != "":
                if line[1:3] == '1.':
                    self.__indexes.append(index)
                elif line[0:8] == 'Pull-out':
                    self.__indexes.append(index - 1)
            index = index + 1
        
        #return len(self.__fileContent)
    
    #----------------------------------------------------------------------------------------------------------------------
    def __extractCurves(self, lineNumbers):

        if len(lineNumbers) == 0:
            return

        speedArray = []
        torqueArray = []
        currentArray = []
        loadArray = []

        for linenumber in range(lineNumbers[0], lineNumbers[1]):
            line = self.__fileContent[linenumber]
            speed = float(line[:8])
            torque = float(line[9:15])
            current = float(line[16:22])
            load = float(line[38:44])

            '''
            speed = line[:8]
            torque = line[9:15]
            current = line[16:22]
            load = line[38:44]
            '''

            speedArray.append(speed)
            torqueArray.append(torque)
            currentArray.append(current)
            loadArray.append(load)
            print(f'{speed}  {torque}  {current}  {load}')
            
        
        curves = Curves()
        curves.speed = speedArray
        curves.torque = torqueArray
        curves.current = currentArray
        curves.load = loadArray

        self.__curves.append(curves)

    #----------------------------------------------------------------------------------------------------------------------
    def __generateCsvFiles(self, eng):
        
        curves1Names = self.__filenames('a',eng)
        curves2Names = self.__filenames('b',eng)
        curves3Names = self.__filenames('c',eng)
        
        if len(self.__curves) == 1:     #This is for when we only have the 100% volts point
            curves1Names = self.__filenames('a',eng)
            self.__saveToCsv(self.__curves[0], curves1Names)

        elif len(self.__curves) == 2:   #This is for when we have the 100% point + one percentage point e.g 0.9
            curves1Names = self.__filenames('a',eng)
            curves2Names = self.__filenames('b',eng)

            self.__saveToCsv(self.__curves[0], curves1Names)
            self.__saveToCsv(self.__curves[1], curves2Names)

        elif len(self.__curves) == 3:   #This is for when we have the 100% point + two percentage points e.g 0.9 and 0.8 

            self.__saveToCsv(self.__curves[0], curves1Names)
            self.__saveToCsv(self.__curves[1], curves2Names)
            self.__saveToCsv(self.__curves[2], curves3Names)

    #----------------------------------------------------------------------------------------------------------------------
    def __filenames(self, letter, eng):
        speedTorque = 'slip_vs_torque_try_' + letter + '_' + eng + '.csv'
        speedCurrent = 'slip_vs_i_try_'+ letter +'_' + eng + '.csv'
        return [speedTorque, speedCurrent]

    #----------------------------------------------------------------------------------------------------------------------
    def __saveToCsv(self, curves, fileNames):
        speedTorquePath = os.path.join(resourcesDirectory, fileNames[0])
        speedCurrentPath = os.path.join(resourcesDirectory, fileNames[1])

        file =  open(speedTorquePath, 'w')
        for index in range(0, len(curves.speed)):    
            file.write("{} {}\n".format(curves.speed[index] , curves.torque[index]))