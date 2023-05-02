import csv
import os
from dataclasses import dataclass
import FTP as ftp
import numpy as np
from scipy.interpolate import make_interp_spline
from datetime import datetime
import time

modelsDirectory = os.path.dirname(__file__)
resourcesDirectory = os.path.join(modelsDirectory, '../../Resources')
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
        self.__noEngineerErrorMessage = "Please selected an Engineer!"
        self.__successfulExportMessage = "Curves have been Exported!"
        self.__failedToImportEdsErrorMessage = "Failed to import EDS Files!"
        self.__noCurveSelectedErrorMessage = "Please select a curve that you like to import from the EDS!"
        self.__edsFilePath = ''
        self.__withstandFilePath = ''
        self.__outputsBasePath = ''
        self.__fullLoadTorque = 0
        self.__fullLoadCurrent = 0
        self.__currentUser = ""

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
    # Checks if the selected Engineer is part of the list of engineers or not
    #----------------------------------------------------------------------------------------------------------------------
    def __engineerExists(self, eng):
        for engineer in self.__engineers:
            if eng in engineer:
                self.__currentUser = engineer     
                return True
        

        raise Exception('Engineer with initials {eng} does not exist!')

    #----------------------------------------------------------------------------------------------------------------------
    def generateCurveFiles(self, eng, edsMain, withstand):
        
        self.__createFilenames(eng)     #Creates all the file names that will be used for saving the csv files
        #Return false if no engineer is selected
        if self.__engineerExists(eng) == False:
            return [False, self.__noEngineerErrorMessage]
        
        if edsMain == 0 and withstand == 0:
            return [False, self.__noCurveSelectedErrorMessage]
        
        importFolder = os.path.join(self.__progInfo[0], eng)
        importEdsFiles = ftp.downloadEdsFiles(eng, importFolder, edsMain, withstand)

        if importEdsFiles[0] == False:
            return [False, self.__failedToImportEdsErrorMessage]
        
        #User is trying to get the current and torque vs speed files from the eds
        if edsMain == 1:
            
            self.__readEDSFile(eng)            
            self.__extractCurrentTorqueCurves()
            #After extracting the curves there should be indexes available
            #to show where the speed vs torque and speed vs current information is
            #If these indexes are empty, then the wrong file was ran
            if len(self.__edsFileIndexes) == 0:
                raise Exception('No datapoints found. Are you sure this is Cage Motor?')

            self.__generateTorqueCurrentSpeedFiles()
            self.__confirmCreationTime(self.__edsfile[0], 'EDS MAIN')

        #User is tring to get the curves from the withstand module
        if withstand == 1:
            
            self.__readWithstandFile(eng)
            self.__extractWithstandCurves()
            self.__generateWithstandFiles()
            self.__confirmCreationTime(self.__withstandFile[0], 'EDS WITHSTAND')

        return [True, self.__successfulExportMessage]
    
    #HANDLES THE STEPS FOR EXTRACTNG CURVES FROM THE EDS FILE
    def __extractCurrentTorqueCurves(self):
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
                    indexOfFLT = line.index('FLT')
                    flt = line[indexOfFLT + 3:]
                    flt = flt[:len(flt)-2]
                    self.__fullLoadTorque = float(flt)
                elif line[0:4] == 'WFAN':
                    indexOfkW = line.index('kW')
                    flc = line[indexOfkW + 2:]
                    flc = flc[:len(flc)-3]
                    self.__fullLoadCurrent = float(flc)
            index = index + 1

    #----------------------------------------------------------------------------------------------------------------------   
    def __readWithstandFile(self, eng):
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
                    if float(self.__withstandFile[index + 1][0:6]) < float(self.__withstandFile[index][0:6]):
                        startingScalerReached = True
                        self.__withstandFileIndexes.append(index)     
                if line[0:28] == 'Current pu     Secs     Mins':    #Determines the row number at which the stall time from hot table starts.          
                    self.__withstandFileIndexes.append(index+1)
                elif line[0:18] == 'Stall Hot and Cold':
                    self.__withstandFileIndexes.append(index)       #Determines the row number at which the stall time from hot and cold table ends.
                elif line[0:21] == 'Current pu  Time Secs':
                    self.__withstandFileIndexes.append(index + 1)   #Determines the row number at which the starting curves start.
                    startingCurvesReached = True
                elif line[0:34] == '       Quoted locked rotor current':
                    self.__withstandStartingCurrentIndex = index
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
        #Start each list with 1 in the zeroth position becase the smoothening function later on will think the first element is not part of the
        #Useful data for the plot
        self.__overloadCurrent = [1] 
        self.__overloadTime = [1] 
        self.__stallColdCurrent = [1]
        self.__stallColdTime = [1]
        self.__stallHotCurrent = [1]
        self.__stallHotTime = [1]
        self.__startOnePuCurrent = [1]
        self.__startOnePuTime = [1]
        self.__startScaledCurrent = [1]
        self.__startScaledTime = [1]

        for lineNumber in range(self.__withstandFileIndexes[0], len(self.__withstandFile)):
            if self.__withstandFile[lineNumber] != "":
                #The first if statement will read the full speed hot curve
                if lineNumber >= self.__withstandFileIndexes[0] and lineNumber < self.__withstandFileIndexes[1]:
                    current = float(self.__withstandFile[lineNumber][0:10])
                    time = float(self.__withstandFile[lineNumber][12:20])
                    self.__overloadCurrent.append(current)
                    self.__overloadTime.append(time)

                if len(self.__withstandFileIndexes) == 4:   #THIS WILL BECOME ACTIVE IF THE USER IS ALSO TRYING TO PLOT THE STARTING CURVES
                    #This part will read the hot and cold stall times
                    if lineNumber >= self.__withstandFileIndexes[1] + 1 and lineNumber < self.__withstandFileIndexes[2] - 2:
                        self.__readStallTimes(lineNumber)
                    #This part will read the starting curves
                    elif lineNumber >= self.__withstandFileIndexes[2] and lineNumber < self.__withstandFileIndexes[3] + 1:
                        current = float(self.__withstandFile[lineNumber][0:5])
                        time = float(self.__withstandFile[lineNumber][6:]) 
                        self.__startOnePuCurrent.append(current)
                        self.__startOnePuTime.append(time)
                    
                    elif lineNumber >= self.__withstandFileIndexes[3] + 1 and lineNumber <= len(self.__withstandFile):
                        current = float(self.__withstandFile[lineNumber][0:5])
                        time = float(self.__withstandFile[lineNumber][6:]) 
                        self.__startScaledCurrent.append(current)
                        self.__startScaledTime.append(time)
                elif len(self.__withstandFileIndexes) == 2:     #THIS WILL BECOME ACTIVE IF THE USER DOES NOT WANT TO PRINT STARTING CURVES
                    if lineNumber >= self.__withstandFileIndexes[1] + 1 and lineNumber <= len(self.__withstandFile):
                        self.__readStallTimes(lineNumber)
                        self.__startOnePuCurrent.append(0)
                        self.__startOnePuTime.append(0)
                        self.__startScaledCurrent.append(0)
                        self.__startScaledTime.append(0)
        #Perform extrapolation to determine the locked rotor point in the starting curves and also determine the volt scaling being used
        if len(self.__withstandFileIndexes) == 4:    
            startingCurrent = self.__withstandFile[self.__withstandStartingCurrentIndex][34:]
            startingCurrent = startingCurrent[:len(startingCurrent) - 2]
            self.__startOnePuCurrent.append(float(startingCurrent))
            self.__startOnePuTime.append(0.1)
            
            startPoint = self.__startingWithstandCurrent(self.__startScaledCurrent, self.__startScaledTime)
            self.__startScaledCurrent.append(startPoint[0])
            self.__startScaledTime.append(startPoint[1])

            point_1 = self.__withstandFile[self.__withstandFileIndexes[2]][:6]
            point_2 = self.__withstandFile[self.__withstandFileIndexes[3]+1][:6]
            scaling = float(point_1) / float(point_2)

            self.__startScaledCurrent[0] = scaling
            self.__startScaledTime[0] = scaling

    #----------------------------------------------------------------------------------------------------------------------------------------
    # Helper function for reading stall times during the process of extracting withstand curves
    #----------------------------------------------------------------------------------------------------------------------------------------    
    def __readStallTimes(self, lineNumber):
        current = float(self.__withstandFile[lineNumber][0:6])
        hotTime = float(self.__withstandFile[lineNumber][7:14])
        coldTime = float(self.__withstandFile[lineNumber][15:21])
                    
        self.__stallHotCurrent.append(current)
        self.__stallColdCurrent.append(current)
        self.__stallHotTime.append(hotTime)
        self.__stallColdTime.append(coldTime)

    #-----------------------------------------------------------------------------------------------------------------------------------------
    # The starting curves in the withstand model do not show the starting current point.
    # We will thus have to do some linear extrapolation to determine the value
    #-----------------------------------------------------------------------------------------------------------------------------------------
    def __startingWithstandCurrent(self, x_values, y_values):
        x_1 = x_values[len(x_values) - 1]
        x_2 = x_values[len(x_values) - 2]

        y_1 = y_values[len(y_values) - 1]
        y_2 = y_values[len(y_values) - 2]

        m = (y_1 - y_2) / (x_1 - x_2)
        c = y_1 - (m * x_1)
        startingTime = 0.1
        startingCurrent = (startingTime-c)/m
        

        return [startingCurrent, startingTime]
    #----------------------------------------------------------------------------------------------------------------------
    #Generates all the required CSV files
    #----------------------------------------------------------------------------------------------------------------------
    def __generateTorqueCurrentSpeedFiles(self):
        
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

        self.__createCSV(self.__loadCurve[0], self.__loadCurve[1], self.__loadPath)     #Create Load Curve file

    def __generateWithstandFiles(self):
        #Save the Full Speed Hot Curve
        self.__createCSV(self.__overloadCurrent, self.__overloadTime, self.__fullSpeedHotStallPath)
        #Save the Cold Stall Time Curve
        self.__createCSV(self.__stallColdCurrent, self.__stallColdTime, self.__coldStallTimePath)
        #Save the Hot Stall Time Curve
        self.__createCSV(self.__stallHotCurrent, self.__stallHotTime, self.__hotStallTimePath)
        #Save the 1 pu starting curve
        specialCurve = True
        self.__createCSV(self.__startOnePuCurrent, self.__startOnePuTime, self.__startOnePuPath, specialCurve)
        #Save the scaled starting curve
        self.__createCSV(self.__startScaledCurrent, self.__startScaledTime, self.__startScaledPath, specialCurve)

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

        self.__fullSpeedHotStallPath = 'overload_'+ eng + ext
        self.__hotStallTimePath = 'hot_stall_' + eng + ext
        self.__coldStallTimePath = 'cold_stall_' + eng + ext
        self.__startOnePuPath = 'start_one_pu_' + eng + ext
        self.__startScaledPath = 'start_scaled_' + eng + ext 

    #----------------------------------------------------------------------------------------------------------------------
    def __createCSV(self, xValues, yValues, fileName, special = False):
        #speedTorquePath = os.path.join(resourcesDirectory, fileNames[0])
        #speedCurrentPath = os.path.join(resourcesDirectory, fileNames[1])
        
        filePath = os.path.join(self.__outputsBasePath, fileName)
        #First convert the lists of x and y values into numpy arrays
        smoothCurve = self.__smoothenCurve(xValues,yValues, special)
        xList = smoothCurve[0]
        yList = smoothCurve[1]

        file =  open(filePath, 'w')
        for index in range(0, len(xList)):    
            file.write("{},{}\n".format(xList[index] , yList[index]))
        
        file.close()

    #Applies a cubic spline interpolation method to smoothen the graphs
    #Take a special argument. If True, then we are doing the start time curve from the withstand and we need to treat it differently
    def __smoothenCurve(self, xValues, yValues, special = False):
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

        #This specia case was created to cater for the starting curve on the withstand model
        xSpecial = 0
        ySpecial = 0
        if special == False:
            x = np.flip(np.array(xValues[1:]))  
            y = np.flip(np.array(yValues[1:]))
        else:
            xSpecial = xValues[1]
            ySpecial = yValues[1]
            x = np.flip(np.array(xValues[2:]))  
            y = np.flip(np.array(yValues[2:]))
            maxSplinePoints = maxSplinePoints - 1

        #First check if the x values are increasing as required to smoothen the curve. 
        #If they are not increasing, the sort them so that they are increasing.
        if (np.diff(x) > 0).all():  #Checks the difference between all the successive elements in the array. If the difference is positve, the array is increasing
            pass
        else:                       #If the array is not increasing as required, then flip it so that it can be increasing.    
            x = np.flip(x)
            y = np.flip(y)

        #Here is where the interpolation actually happens.
        #Do it for max elements - 1 to reserve space for the voltage scaling value for curves that use it otherwise the first 
        #element of the original curve will be used.
        x_y_Spline = make_interp_spline(x, y)
        X_ = np.linspace(x.min(), x.max(), maxSplinePoints - 1)
        Y_ = x_y_Spline(X_)

        #Return the data back to lists and then add back the first element which could be the voltage scaling in some instances.
        xList = X_.tolist()
        yList = Y_.tolist()

        #The withstand curves really need special handling
        if special == True:
            xList.insert(0, xSpecial)
            yList.insert(0, ySpecial)
            yList[len(yList) - 2] = yList[len(yList) - 1] 
            

        xList.insert(0, title)
        yList.insert(0, title)
        if str(xValues[0]) == load:
            xList[len(xList) - 1] = xValues[1]
            yList[len(yList) - 1] = stiction

        return [xList, yList]

    #Checks how long ago the EDS file was ran. If it was ran more than 5 minutes ago, an exception will be thrown and the user will 
    #be asked to re-run the eds file
    def __confirmCreationTime(self, firstLine, fileName):
        maxTimeDelayMinutes = 5
        indexOfDash = self.__currentUser.index('-')
        user = self.__currentUser[indexOfDash + 1:]
        indexOfUser = firstLine.index(user)
        indexOfPage = firstLine.index('PAGE')
        fileDate = firstLine[indexOfUser + len(user):indexOfPage]
        fileDate = fileDate.strip()
        indexOfSpace = fileDate.rindex(' ')
        fileDate = fileDate[indexOfSpace:]
        fileDate = fileDate.strip()
        fileCreationTime = datetime.strptime(fileDate, "%H:%M")
        
        timeNowString = datetime.today().strftime('%H:%M') 
        timeNow = datetime.today().strptime(timeNowString, '%H:%M')

        deltaT = timeNow - fileCreationTime
        deltaTMinutes = deltaT.total_seconds()/60
        
        if deltaTMinutes > maxTimeDelayMinutes:
            raise TimeDiferenceError(maxTimeDelayMinutes, deltaTMinutes, fileName)

class TimeDiferenceError(Exception):
    def __init__(self, maxTime, elapsedTime, fileName):
        self.message = f"""The {fileName} file you was ran {elapsedTime} minutes ago. 
Files should be imported within {maxTime} minutes of running. 
Please re-run the eds module to ensure you have the latest file.

If you are sure that you are importing the correct file,
Ignore this error."""

        super().__init__(self.message)
        
        
#if __name__ == '__main__':
#    model = Model()
#    model.generateCurveFiles('GM')
