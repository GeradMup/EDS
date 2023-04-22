import csv
import os
from dataclasses import dataclass
import FTP as ftp
import numpy as np
from scipy.interpolate import make_interp_spline

modelsDirectory = os.path.dirname(__file__)
resourcesDirectory = os.path.join(modelsDirectory, '../../Resources')
edsFolder = 'C:/EDS PLOTS'
pathToEDSFile = os.path.join(resourcesDirectory, '%T.MAIN')

pathToEngineers = os.path.join(resourcesDirectory, 'Engineers.txt')
pathToProgInfo = os.path.join(resourcesDirectory, 'ProgInfo.txt')

#----------------------------------------------------------------------------------------------------------------------
@dataclass
class Curves():
    speed = []
    torque = []
    current = []

#----------------------------------------------------------------------------------------------------------------------
class Model():
    def __init__(self):
        self.__edsFileIndexes = []
        self.__withstandFileIndexes = []
        self.__curves = []
        self.__loadCurve = []
        self.__engineers = []
        self.__fullSpeedStallCurrent = []
        self.__fullSpeedStallTime = []
        self.__noEngineerErrorMessage = "Please selected an Engineer!"
        self.__successfulExportMessage = "Curves have been Exported!"
        self.__failedToImportEdsErrorMessage = "Failed to import EDS Files!"
        self.__noCurveSelectedErrorMessage = "Please select a curve that you like to import from the EDS!"
        self.__edsFilePath = ''
        self.__withstandFilePath = ''
        self.__outputsBasePath = ''
        self.__fullLoadTorque = 0
        self.__fullLoadCurrent = 0

        self.__readResources()
    
    #----------------------------------------------------------------------------------------------------------------------
    # Reads all the required external resources 
    #----------------------------------------------------------------------------------------------------------------------
    def __readResources(self):
        engineersFile = open(pathToEngineers, 'r') 
        self.__engineers = engineersFile.read().split('\n')
        engineersFile.close()

        progInfoFile = open(pathToProgInfo, 'r')
        self.__progInfo = progInfoFile.read().split('\n')
        progInfoFile.close() 
        self.__outputsBasePath = self.__progInfo[1]

    #----------------------------------------------------------------------------------------------------------------------
    def getEngineers(self):
        return self.__engineers

    #----------------------------------------------------------------------------------------------------------------------
    def generateCurveFiles(self, eng, currentTorqueSpeed, withstand):
        #Return false if no engineer is selected
        if self.__engineerExists(eng) == False:
            return [False, self.__noEngineerErrorMessage]
        
        if currentTorqueSpeed == 0 and withstand == 0:
            return [False, self.__noCurveSelectedErrorMessage]
        '''
        importFolder = os.path.join(self.__progInfo[0], eng)
        importEdsFiles = ftp.downloadEdsFiles(eng, importFolder, currentTorqueSpeed, withstand)

        if importEdsFiles[0] == False:
            return [False, self.__failedToImportEdsErrorMessage]
        '''
        
        #Read the Main File with all the design parameters
        self.__readEDSFile(eng)
        self.__readWithstandFile(eng)

        curve1LineNumbers = []
        curve2LineNumbers = []
        curve3LineNumbers = []

        if len(self.__edsFileIndexes) == 6:        #All three voltage points avaiable: 100%, first percentage and second percentage
            curve1LineNumbers = [self.__edsFileIndexes[0], self.__edsFileIndexes[1]]
            curve2LineNumbers = [self.__edsFileIndexes[2], self.__edsFileIndexes[3]]
            curve3LineNumbers = [self.__edsFileIndexes[4], self.__edsFileIndexes[5]]

        elif len(self.__edsFileIndexes) == 4:      #Only two voltage points available. 100% and first percentage     
            curve1LineNumbers = [self.__edsFileIndexes[0], self.__edsFileIndexes[1]]
            curve2LineNumbers = [self.__edsFileIndexes[2], self.__edsFileIndexes[3]]
        
        elif len(self.__edsFileIndexes) == 2:      #Only the 100% Voltage point is available
            curve1LineNumbers = [self.__edsFileIndexes[0], self.__edsFileIndexes[1]]
        
        self.__extractEDSCurves(curve1LineNumbers)
        self.__extractEDSCurves(curve2LineNumbers)
        self.__extractEDSCurves(curve3LineNumbers)
        self.__extractWithstandCurves()

        self.__generateCsvFiles(eng)

        return [True, self.__successfulExportMessage]
    
    #----------------------------------------------------------------------------------------------------------------------
    # Checks if the selected Engineer is part of the list of engineers or not
    #----------------------------------------------------------------------------------------------------------------------
    def __engineerExists(self, eng):
        if eng in self.__engineers:     
            return True
        else:
            return False

    #----------------------------------------------------------------------------------------------------------------------    
    def __readEDSFile(self, eng):
        #First we will read the EDS file and process it
        self.__edsFilePath = os.path.join(self.__progInfo[0], eng, '%T.MAIN')
        edsfile = open(self.__edsFilePath, 'r')
        self.__edsfile = edsfile.read().split('\n')
        edsfile.close()

        index = 0
        self.__edsFileIndexes.clear()
        for line in self.__edsfile:
            if line != "":
                if line[1:3] == '1.':                           #Determines the row number at which the run up table starts in the main file.          
                    self.__edsFileIndexes.append(index)
                elif line[0:8] == 'Pull-out':
                    self.__edsFileIndexes.append(index - 1)     #Determines the row number at which the run up table ends in the main file.
                elif line[0:8] == 'kW/m2 AC':                   #Determines the row number where the full load torque can be found
                    flt = line[39:]
                    flt = flt[:len(flt)-2]
                    self.__fullLoadTorque = float(flt)
                elif line[0:4] == 'WFAN':
                    flc = line[61:]
                    flc = flc[:len(flc)-3]
                    self.__fullLoadCurrent = float(flc)
            index = index + 1

    #----------------------------------------------------------------------------------------------------------------------   
    def __readWithstandFile(self, eng):
        #Next we will read the withstand model file and process it
        self.__withstandFilePath = os.path.join(self.__progInfo[0], eng, '%T.WTHSTND')
        withstandFile = open(self.__withstandFilePath, 'r')
        self.__withstandFile = withstandFile.read().split('\n')
        withstandFile.close()

        index = 0
        self.__withstandFileIndexes.clear()
        startingCurvesReached = False
        startingScalerReached = False
        for line in self.__withstandFile:
            if line != "":
                if startingCurvesReached == True and startingScalerReached == False:                   #Determine the position at which the first scaler for the starting curve is        
                    if float(self.__withstandFile[index + 1][0:6]) > float(self.__withstandFile[index][0:6]):
                        startingScalerReached = True
                        self.__withstandFileIndexes.append(index)     
                if line[0:28] == 'Current pu     Secs     Mins':    #Determines the row number at which the stall time from hot table starts.          
                    self.__withstandFileIndexes.append(index+1)
                elif line[0:18] == 'Stall Hot and Cold':
                    self.__withstandFileIndexes.append(index)       #Determines the row number at which the stall time from hot and cold table ends.
                elif line[0:21] == 'Current pu  Time Secs':
                    self.__withstandFileIndexes.append(index + 1)   #Determines the row number at which the starting curves start.
                    startingCurvesReached = True
            index = index + 1

    #----------------------------------------------------------------------------------------------------------------------------------------
    # Reads through EDS file and extracts the curves as required
    #----------------------------------------------------------------------------------------------------------------------------------------
    def __extractEDSCurves(self, lineNumbers):

        if len(lineNumbers) == 0:
            return

        speedArray = []
        torqueArray = []
        currentArray = []
        self.__loadCurve = []
        loadSpeed = []
        loadTorque = []

        voltPoint = float(self.__edsfile[lineNumbers[0] - 4][37:41])
        speedArray.append(voltPoint)
        torqueArray.append(voltPoint)
        currentArray.append(voltPoint)
        loadSpeed.append('Load')
        loadTorque.append('Load')

        for linenumber in range(lineNumbers[0], lineNumbers[1]):
            line = self.__edsfile[linenumber]
            speed = float(line[:8])
            torque = float(line[9:15]) * self.__fullLoadTorque
            current = float(line[16:22]) * self.__fullLoadCurrent
            load = float(line[38:44])

            speedArray.append(speed)
            torqueArray.append(torque)
            currentArray.append(current)
            loadTorque.append(load)
            loadSpeed.append(speed)

        self.__loadCurve = [loadSpeed, loadTorque]   
            
        curves = Curves()
        curves.speed = speedArray
        curves.torque = torqueArray
        curves.current = currentArray

        self.__curves.append(curves)

    #----------------------------------------------------------------------------------------------------------------------------------------
    # Reads through WTHSTND file and extracts the curves as required
    #----------------------------------------------------------------------------------------------------------------------------------------
    def __extractWithstandCurves(self):
        self.__fullSpeedStallCurrent = [] 
        self.__fullSpeedStallTime = [] 
        self.__stallColdCurrent = []
        self.__stallColdTime = []
        self.__stallHotCurrent = []
        self.__stallHotTime = []
        self.__startOnePuCurrent = []
        self.__startOnePuTime = []
        self.__startScalerPuCurrent = []
        self.__startScalerPuTime = []

        fullLoadHotStart = self.__withstandFileIndexes[0]
        fullLoadHotEnd = self.__withstandFileIndexes[1]
        stallStart = self.__withstandFileIndexes[1] + 1
        stallEnd = self.__withstandFileIndexes[1]

        for lineNumber in range(self.__withstandFileIndexes[0], len(self.__withstandFile) - 1):
            if lineNumber >= fullLoadHotStart and lineNumber < fullLoadHotEnd:
                current = float(self.__withstandFile[lineNumber][0:10])
                time = float(self.__withstandFile[lineNumber][12:20])
                self.__fullSpeedStallCurrent.append(current)
                self.__fullSpeedStallTime.append(time)

        print(self.__fullSpeedStallCurrent)
        print(self.__fullSpeedStallTime)
        
        '''
        for linenumber in range(self.__withstandFileIndexes[0], len(self.__withstandFile)-1):
            #The first if statement will read Full Speed Hot Curve
            if linenumber >= self.__withstandFileIndexes[0] and linenumber < self.__withstandFileIndexes[1]:
                current = self.__withstandFile[linenumber][3:9]
                time = self.__withstandFile[linenumber][13:20]
            
                self.__fullSpeedStallCurrent.append(float(current))
                self.__fullSpeedStallTime.append(float(time))
            else:   
                #The else section reads the Hot and Cold Stall time curves 
                if linenumber > self.__withstandFileIndexes[1]:
                    current = self.__withstandFile[linenumber][0:6]
                    hotTime = self.__withstandFile[linenumber][8:14]
                    coldTime = self.__withstandFile[linenumber][16:21]

                    self.__stallCurrent.append(float(current))
                    self.__hotStallTime.append(float(hotTime))
                    self.__coldStallTime.append(float(coldTime))
                    #print(f'{current} {hotTime} {coldTime}')
            '''
    #----------------------------------------------------------------------------------------------------------------------
    #Generates all the required CSV files
    #----------------------------------------------------------------------------------------------------------------------
    def __generateCsvFiles(self, eng):
        
        self.__createFilenames(eng)     #Creates all the file names that will be used for saving the csv files
        
        if len(self.__curves) == 1:     #This is for when we only have the 100% volts point
            self.__addZeroes()          #Fill the rest of the positions with zeroes
            self.__addZeroes()

        elif len(self.__curves) == 2:   #This is for when we have the 100% point + one percentage point e.g 0.9
            self.__addZeroes()          #Fill the rest of the positions with zeroes

        elif len(self.__curves) == 3:   #This is for when we have the 100% point + two percentage points e.g 0.9 and 0.8 
            pass

        self.__createCSV(self.__curves[0].speed, self.__curves[0].torque, self.__speedTorque1Path)   #Speed vs Torque at 1pu
        self.__createCSV(self.__curves[0].speed, self.__curves[0].current, self.__speedCurrent1Path)   #Speed vs Current at 1pu

        self.__createCSV(self.__curves[1].speed, self.__curves[1].torque, self.__speedTorque2Path)   #Speed vs Torque at first scaler
        self.__createCSV(self.__curves[1].speed, self.__curves[1].current, self.__speedCurrent2Path)   #Speed vs Current at first scaler

        self.__createCSV(self.__curves[2].speed, self.__curves[2].torque, self.__speedTorque3Path)   #Speed vs Torque at second scaler
        self.__createCSV(self.__curves[2].speed, self.__curves[2].current, self.__speedCurrent3Path)   #Speed vs Current at second scaler

        self.__createCSV(self.__loadCurve[0], self.__loadCurve[1], self.__loadPath)

        #Save the Full Speed Hot Stall Time Curve
        #self.__createCSV(self.__fullSpeedStallCurrent, self.__fullSpeedStallTime, self.__fullSpeedHotStallPath)
        #Save the Cold Stall Time Curve
        #self.__createCSV(self.__stallCurrent, self.__coldStallTime, self.__coldStallTimePath)
        #Save the Hot Stall Time Curve
        #self.__createCSV(self.__stallCurrent, self.__hotStallTime, self.__hotStallTimePath)

    #----------------------------------------------------------------------------------------------------------------------
    #Creates a curve with zeroes. This is used if the user choose to ommit some of the voltage scalers: nvolt = 1 or nvolt = 2
    #----------------------------------------------------------------------------------------------------------------------
    def __addZeroes(self):
        speed = self.__curves[0].speed
        zeros = [0.0] * len(speed) 
        newCurvesSet = Curves()
        newCurvesSet.speed = zeros
        newCurvesSet.current = zeros
        newCurvesSet.torque = zeros

        self.__curves.append(newCurvesSet)

    #----------------------------------------------------------------------------------------------------------------------
    #Function to create all the file names that will be used to create the csv files
    #----------------------------------------------------------------------------------------------------------------------
    def __createFilenames(self, eng):
        ext = '.csv'
        self.__speedTorque1Path = 'slip_vs_torque_a' + '_' + eng + ext
        self.__speedCurrent1Path = 'slip_vs_i_a' + '_' + eng + ext

        self.__speedTorque2Path = 'slip_vs_torque_b' + '_' + eng + ext
        self.__speedCurrent2Path = 'slip_vs_i_b' + '_' + eng + ext

        self.__speedTorque3Path = 'slip_vs_torque_c' + '_' + eng + ext
        self.__speedCurrent3Path = 'slip_vs_i_c' + '_' + eng + ext
        
        self.__loadPath = 'slip_vs_load_' + eng + ext

        self.__fullSpeedHotStallPath = 'full_speed_hot_stall_time_'+ eng + ext
        self.__hotStallTimePath = 'hot_stall_time_' + eng + ext
        self.__coldStallTimePath = 'cold_stall_time_' + eng + ext 

    #----------------------------------------------------------------------------------------------------------------------
    def __createCSV(self, xValues, yValues, fileName):
        #speedTorquePath = os.path.join(resourcesDirectory, fileNames[0])
        #speedCurrentPath = os.path.join(resourcesDirectory, fileNames[1])
        
        filePath = os.path.join(self.__outputsBasePath, fileName)
        #First convert the lists of x and y values into numpy arrays
        smoothCurve = self.__smoothenCurve(xValues,yValues)
        xList = smoothCurve[0]
        yList = smoothCurve[1]

        file =  open(filePath, 'w')
        for index in range(0, len(xList)):    
            file.write("{},{}\n".format(xList[index] , yList[index]))
        
        file.close()

    def __smoothenCurve(self, xValues, yValues):
        xList = []
        yList = []
        load = 'Load'
        maxSplinePoints = 200
        #If the curve contains all zeroes then we will not perform smoothening on it
        if xValues[2] == 0:
            xList = [0] * (maxSplinePoints)
            yList = [0] * (maxSplinePoints)
            return [xList, yList]
        stiction = 0
        #Read the x and y values but leave out the first element because it contains information about volt scalings
        title = xValues[0]
        if str(xValues[0]) == load:
            stiction = yValues[1]
            yValues[1] = 0
            title = load
    
        x = np.flip(np.array(xValues[1:]))  
        y = np.flip(np.array(yValues[1:]))

        #Here is where the interpolation actually happens.
        #Do it for max elements - 1 to reserve space for the voltage scaling value for curves that use it otherwise the first 
        #element of the original curve will be used.
        x_y_Spline = make_interp_spline(x, y)
        X_ = np.linspace(x.min(), x.max(), maxSplinePoints - 1)
        Y_ = x_y_Spline(X_)

        #Return the data back to lists and then add back the first element which could be the voltage scaling in some instances.
        xList = X_.tolist()
        yList = Y_.tolist()
        xList.insert(0, title)
        yList.insert(0, title)
        if str(xValues[0]) == load:
            xList[len(xList) - 1] = xValues[1]
            yList[len(yList) - 1] = stiction

        return [xList, yList]

#if __name__ == '__main__':
#    model = Model()
#    model.generateCurveFiles('GM')
