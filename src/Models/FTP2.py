import ftplib 
from dataclasses import dataclass
from tkinter import Tk, filedialog
from fpdf import FPDF
import os


@dataclass
class Credentials():
    userame:str = ""
    password:str = ""
    port:int = 0
    hostname:str = ""
    usefolder:str = ""
    fullname: str = ""

def getFolderName():
    root = Tk() # pointing root to Tk() to use it as Tk() in program.
    root.withdraw() # Hides small tkinter window.

    root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    folder = filedialog.askdirectory() # Returns opened path as str
    print(folder)
    return folder

def addPage(pdf):
    pdf.add_page()
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Courier", size = 11.1)
    pdf.set_margins(10,10)
    # open the text file in read mode

def saveAsPdf(textFilePath, pdfFilePath, engineerName, withstand = 0):
    
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()  
    cellWidth = 200
    cellDepth = 4.1
    # Add a page
    addPage(pdf)
    pdf.cell(cellWidth, cellDepth, txt = f'    {engineerName}', ln = 1, align = 'L')

    file = open(textFilePath, "r")

    # insert the texts in pdf
    lineBreakCharCode = 12
    minLinesBeforePageBreak = 0
    for index, line in enumerate(file):
        if ord(line[0]) == lineBreakCharCode and index > minLinesBeforePageBreak:
            #print(f'{line[0]} {ord(line[0])} index = {index}')
            addPage(pdf)
            pdf.cell(cellWidth, cellDepth, txt = f' {engineerName}', ln = 1, align = 'L')
        
        if withstand == 1 and line[:15] == 'Starting curves':
           addPage(pdf) 
   
        pdf.cell(cellWidth, cellDepth, txt = line, ln = 1, align = 'L')
    
    # save the pdf with name .pdf
    pdf.output(pdfFilePath) 
    file.close()

    #delete the source file
    os.remove(textFilePath) 


def downloadEdsFiles(eng, jobNumber, currentTorqueSpeed, withstand):
    #Connection parameters
    credentials = getLoginCredentials(eng)
    outputsFolder = getFolderName()

    #creat an FTP client instance, use the timeout(seconds) parameter for slow connections
    ftp = ftplib.FTP(timeout=30)

    #connect to the FTP server
    ftp.connect(credentials.hostname, credentials.port)

    #login to the server.
    ftp.login(credentials.userame, credentials.password)
    #ftp.prot_p()

    #Some servers are configured to only accept only SSL connections
    #change the connections to the following
    #ftp = ftplib.FTP_TLS(timeout = 30)
    #ftp.prot_p()       =>    This line must go after logging in

    #Navigate to the correct directory on the server

    #Display all the filenames in the current working directory
    #filenames = ftp.nlst()
    #print(filenames)

    #DEFINE ALL THE PATHS HERE
    mainFilename = '%T.MAIN'
    pathToSaveMainFile = outputsFolder + '\\' + mainFilename
    pathToMainPdfFile = f'{outputsFolder}\{jobNumber} EDS MAIN.pdf'
    
    withstandFileName = '%T.WTHSTND'
    pathToSaveWithstandFile = outputsFolder + '\\' + withstandFileName
    pathToWithstandPdfFile = f'{outputsFolder}\{jobNumber} EDS WITHSTAND.pdf'

    
    if currentTorqueSpeed == 1:
        with open(pathToSaveMainFile, 'wb') as file:
            returnCode = ftp.retrbinary(f"RETR {mainFilename}", file.write)
        
        saveAsPdf(pathToSaveMainFile, pathToMainPdfFile, credentials.fullname)

    if withstand == 1:
        with open(pathToSaveWithstandFile, 'wb') as file:
            returnCode = ftp.retrbinary(f"RETR {withstandFileName}", file.write)

        saveAsPdf(pathToSaveWithstandFile, pathToWithstandPdfFile, credentials.fullname, withstand)
    ftp.close()

    if returnCode.startswith("226"):
        return [True, '']
    else:
        return [True, 'Failed to download eds file']
    
    

def getLoginCredentials(eng):
    credentials = Credentials()
    credentials.port = 21
    credentials.hostname = 'eds_1'
    baseFolder = 'home/users'
    
    
    if eng == 'GM':
        credentials.userame = 'kg'
        credentials.password = 'krakus'
        credentials.fullname = "Gerad Mupfumisi"
        
    elif eng == 'PMV':
        credentials.userame = 'pmv'
        credentials.password = 'viool'
        credentials.fullname = "Martin Viljoen"

    elif eng == 'DM':
        credentials.userame = 'mkm'
        credentials.password = 'Keletso01'
        credentials.fullname = "Dirren Moodley"
    
    elif eng == 'PR':
        credentials.userame = 'ra'
        credentials.password = 'skud'
        credentials.fullname = 'Percy Rabosiwana'
    
    elif eng == 'DW':
        credentials.userame = 'kg'
        credentials.password = 'kgodyn'
        credentials.fullname = 'Derek Wood'
    
    elif eng == 'JN':
        credentials.userame = 'kg'
        credentials.password = 'kgodyn'
        credentials.fullname = 'Johhny Nunes'

    return credentials


