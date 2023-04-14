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
#from views import *
#from Models import *

class Controller():
    def __init__(self):
        self.__eventHandlers = []
        self.__eventHandlers.append(self.__enterKey)
        self.__eventHandlers.append(self.__selectedEng)

        self.__views = views.Views(self.__eventHandlers)
        self.__model = model.Model()

        self.__window = self.__views.getWindow()

        #Set this to blank initially
        self.__engineer=""

    #Method called whenever the up arrow is pressed on the keyboard
    def __enterKey(self):
        self.__engineer = self.__views.getEngineer()
        self.__torqueSpeed = self.__views.getTorqueSpeed()
        self.__currentSpeed = self.__views.getCurrentSpeed()
        self.__withstandTime = self.__views.getWithstandTime()
        self.__criticalSpeed = self.__views.getCriticalSpeed()
 
        curvesGenerated = self.__model.generateCurveFiles(self.__engineer)

        if curvesGenerated[0] == False:
            self.__views.showError(curvesGenerated[1]) 
        else:
            self.__views.showInfo(curvesGenerated[1])

    #Callback method for when the engineers option box changes
    def __selectedEng(self, eng):
        self.__engineer = eng

    def launch(self):
        self.__window.mainloop()


if __name__ == '__main__':
    controller = Controller()
    controller.launch()