from tkinter import *
from tkinter import messagebox

class Views():
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Event Handlers will be call back functions that will be called when events happen on the window
    def __init__(self, eventHandlers = []):
        self.__createWindow()   #Creates the main window

        self.__selectedEngineer = StringVar()
        self.__torqueSpeedSelected = IntVar()
        self.__currentSpeedSelected = IntVar()
        self.__withstandTimeSelected = IntVar()
        self.__criticalSpeedSelected = IntVar()

        self.__enterButtonCallback = eventHandlers[0]
        self.__optionChangeCallback = eventHandlers[1]

        self.__addButton()
        self.__addDropdownMenu(['DW','PMV','PR','DM','GM'])
        self.__addCheckboxes()

        self.__placeWidgets()


    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def __createWindow(self):
        #Creates the Main Window
        self.__mainWindow = Tk()
        self.__mainWindow.eval('tk::PlaceWindow . center')      #Place window in the center of the screen

        self.__mainWindow.geometry("500x300")           #sets the window size (Length x Height)
        self.__mainWindow.resizable(False, False)       #Users cannot resize either the length or width of the window
        self.__mainWindow.title("EDS Curves Version 0.1")
        self.__backgroundColour = "#%02x%02x%02x" % (240, 240, 237)
        self.__mainWindow.configure(bg=self.__backgroundColour)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getEngineer(self):
        return self.__selectedEngineer.get()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getTorqueSpeed(self):
        return self.__torqueSpeedSelected.get()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getCurrentSpeed(self):
        return self.__currentSpeedSelected.get()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getWithstandTime(self):
        return self.__withstandTimeSelected.get()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def getCriticalSpeed(self):
        return self.__criticalSpeedSelected.get()
    
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
        self.__okButton.place(x=20,y=230)
        self.__dropdownMenu.place(x=20,y=190)
        #self.__torqueSpeedCheck.place(x=20, y=20)
        #self.__currentSpeedCheck.place(x=20,y=50)
        #self.__withstandCheck.place(x=20,y=80)
        #self.__criticalSpeedCheck.place(x=20,y=110)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Add a button to the window
    def __addButton(self):
        self.__okButton = Button(
            self.__mainWindow, 
            text = "EXPORT CURVES", 
            command = self.__enterButtonCallback,
            height = 2,
            width = 15,
            font = ('consolas 12 bold'),         #Font size and font type
            justify=CENTER,
            )
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #Add a drop down menu to place all the engineers' names
    def __addDropdownMenu(self, options):
        self.__dropdownMenu = OptionMenu(
            self.__mainWindow, 
            self.__selectedEngineer,   #Variable to store the selected engineer's name
            *options,
            #command=self.__optionChangeCallback
            )

    def __addCheckboxes(self):
        self.__torqueSpeedCheck = Checkbutton(
            self.__mainWindow, 
            text='Torque vs Speed',
            variable=self.__torqueSpeedSelected,    #variable to store the state of the checkbox
            onvalue=1, 
            offvalue=0,
            font='Consolas 12'
            )
        
        self.__currentSpeedCheck = Checkbutton(
            self.__mainWindow, 
            text='Current vs Speed',
            variable=self.__currentSpeedSelected,   #variable to store the state of the checkbox
            onvalue=1, 
            offvalue=0,
            font='Consolas 12'
            )
        
        self.__withstandCheck = Checkbutton(
            self.__mainWindow, 
            text='Withstnad vs Time',
            variable=self.__withstandTimeSelected,  #variable to store the state of the checkbox
            onvalue=1, 
            offvalue=0,
            font='Consolas 12'
            )
        
        self.__criticalSpeedCheck = Checkbutton(
            self.__mainWindow, 
            text='Speed vs Torque',
            variable = self.__criticalSpeedSelected,    #variable to store the state of the checkbox
            onvalue=1, 
            offvalue=0,
            font='Consolas 12'
            )

    #-----------------------------------------------------------------------------------------------------------------------------------------------   
    def showError(self, message):
        messagebox.showerror("Error", message)

    #-----------------------------------------------------------------------------------------------------------------------------------------------
    def showInfo(self, message):
        messagebox.showinfo("Success", message)

    # -----------------------------------------------------------------------------------------------------------------------------------------------   

    