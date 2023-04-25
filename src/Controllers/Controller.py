import sys
import os


#First let's the establish the path to the views and the models folder
controllersDirectory = os.path.dirname(__file__)
viewsDirectory = os.path.join(controllersDirectory, '../Views')
modelsDirectory = os.path.join(controllersDirectory, '../Models')
sys.path.append(viewsDirectory)
sys.path.append(modelsDirectory)

#Now import main models, main views and other sub classes
import Views as views
import Models as model
import ErrorWindow as errorWin
#from views import *
#from Models import *

class Controller():
    def __init__(self):
        self.__eventHandlers = []
        self.__eventHandlers.append(self.__enterKey)
        self.__eventHandlers.append(self.__selectedEng)
        #TAKE OUT EVERYTHING TO DO WITH VIEWS BECAUSE WE ARE NOW CALLING THIS WHOLE PROGRAM FROM EXCEL VBA (LX22)
        self.__model = model.Model()
        
        #self.__views = views.Views(self.__eventHandlers, self.__model.getEngineers())
        
        #self.__window = self.__views.getWindow()

        #Read system arguments to get the required details before running the rest of the script
        #self.__engineer = sys.argv[1]
        #self.__currentTorqueSpeed = int(sys.argv[2])
        #self.__withstandTime = int(sys.argv[3])

        #self.__engineer = 'GM'
        #self.__currentTorqueSpeed = 1
        #self.__withstandTime = 0

        self.__enterKey()   #This function was originally designed to work with the tkinter gui

    #Method called whenever the up arrow is pressed on the keyboard
    def __enterKey(self):
        #self.__engineer = self.__views.getEngineer()
        #currentTorqueSpeed = self.__views.getCurrentTorqueSpeed()
        #withstand = self.__views.getWithstandTime()
        #curvesGenerated = self.__model.generateCurveFiles(self.__engineer, currentTorqueSpeed, withstand)
        try:
            #curvesGenerated = self.__model.generateCurveFiles(self.__engineer, self.__currentTorqueSpeed, self.__withstandTime)
            self.__model.generateCurveFiles('GM', 1, 1)
        except Exception as exc:
            self.__errors = errorWin.ErrorWindow()
            self.__errors.showException(exc)
        #nothing = input("Done")

        '''
        if curvesGenerated[0] == False:
            self.__views.showError(curvesGenerated[1]) 
        else:
            self.__views.showInfo(curvesGenerated[1])
            self.__window.quit()
        '''

    #Callback method for when the engineers option box changes
    def __selectedEng(self, eng):
        self.__engineer = eng

    def launch(self):
        self.__window.mainloop()


if __name__ == '__main__':
    controller = Controller()
    #controller.launch()