from tkinter import *
from tkinter import messagebox

class Views():
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Event Handlers will be call back functions that will be called when events happen on the window
    def __init__(self, eventHandlers = []):
        self.__createWindow()

        self.__enterButtonCallback = eventHandlers[0]
        self.__optionChangeCallback = eventHandlers[1]

        self.__addButton()
        self.__addDropdownMenu(['DW','PMV','PR','DM','GM'])

        self.__placeWidgets()

        self.selectedEngineer = ""
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def __createWindow(self):
        #Creates the Main Window
        self.__mainWindow = Tk()
        self.__mainWindow.eval('tk::PlaceWindow . center')      #Place window in the center of the screen

        self.__mainWindow.geometry("500x200")           #sets the window size (Length x Height)
        self.__mainWindow.resizable(False, False)       #Users cannot resize either the length or width of the window
        self.__mainWindow.title("EDS Curves Version 0.1")
        self.__backgroundColour = "#%02x%02x%02x" % (240, 240, 237)
        self.__mainWindow.configure(bg=self.__backgroundColour)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getWindow(self):
        return self.__mainWindow
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getOkButton(self):
        return self.__okButton
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getDropdownMenu(self):
        return self.__dropdownMenu

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def __placeWidgets(self):
        self.__okButton.place(x=130,y=60)
        self.__dropdownMenu.place(x=130,y=20)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Add a button to the window
    def __addButton(self):
        self.__okButton = Button(
            self.__mainWindow, 
            text = "EXPORT CURVES", 
            command = self.__enterButtonCallback,
            height = 3,
            width = 20,
            font = ('consolas 15 bold'),         #Font size and font type
            justify=CENTER,
            )
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Add a drop down menu to place all the engineers' names
    def __addDropdownMenu(self, options):
        self.__dropdownMenu = OptionMenu(
            self.__mainWindow, 
            StringVar(), 
            *options,
            command=self.__optionChangeCallback
            )

    #-----------------------------------------------------------------------------------------------------------------------------------------------   
    def showError(self, message):
        messagebox.showerror("Error", message)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def showInfo(self, message):
        messagebox.showinfo("Success", message)

    # -----------------------------------------------------------------------------------------------------------------------------------------------   

    