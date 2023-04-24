from tkinter import *
import traceback

#THIS CLASS IS FOR SHOWING POP UP MESSAGES WHENEVER AN ERROR OCCURS DURING EXCECUTION OF A PYTHON SCRIPT
class ErrorWindow():
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        #Creates the Main Window
        self.__mainWindow = Tk()
        self.__mainWindow.eval('tk::PlaceWindow . center')      #Place window in the center of the screen

        self.__mainWindow.geometry("800x400")           #sets the window size (Length x Height)
        self.__mainWindow.resizable(False, False)       #Users cannot resize either the length or width of the window
        self.__mainWindow.title("ERROR")
        self.__backgroundColour = "#%02x%02x%02x" % (252, 3, 3)
        self.__mainWindow.configure(bg=self.__backgroundColour)

        self.__textbox = Text(self.__mainWindow, height=15, width=68, font=('Consolas 15'))
        self.__textbox.place(x=20,y=20)
    

    def showException(self, exc):
        exceptionName = type(exc).__name__
        fullTraceback = traceback.format_exc()

        allIndexes = [i for i in range(len(fullTraceback)) if fullTraceback.startswith('File ', i)]
        index = allIndexes[len(allIndexes) - 1]
        indexOfExceptionType = [i for i in range(len(fullTraceback)) if fullTraceback.startswith(f'{exceptionName}', i)][0]

        exceptionString = f'{exceptionName} \n\n\n {exc} \n\n\n {fullTraceback[index:indexOfExceptionType]}'

        self.__textbox.configure(state='normal')
        self.__textbox.insert(END, exceptionString)
        self.__textbox.configure(state='disabled')
        self.__mainWindow.mainloop()
        pass