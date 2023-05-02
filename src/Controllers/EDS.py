
#THIS IS THE MAIN FILE THAT WILL RUN WHEN USERS ARE TRYING TO IMPORT EDS FILES TO SAVE THEM AS PDF
import sys
import os


#First let's the establish the path to the views and the models folder
controllersDirectory = os.path.dirname(__file__)
viewsDirectory = os.path.join(controllersDirectory, '../Views')
modelsDirectory = os.path.join(controllersDirectory, '../Models')

sys.path.append(viewsDirectory)
sys.path.append(modelsDirectory)

import ErrorWindow as errorWin
import FTP2 as ftp2

class eds():
    def __init__(self):
        try:
            engineer = sys.argv[1]
            jobNumber = sys.argv[2]
            mainFile = int(sys.argv[3])
            withstandFile = int(sys.argv[4])
            ftp2.downloadEdsFiles(engineer, jobNumber, mainFile, withstandFile)
        except Exception as exc:
            errorWindow = errorWin.ErrorWindow()
            errorWindow.showException(exc)
if __name__=='__main__':
    eds = eds()
