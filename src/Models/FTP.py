import ftplib 
from dataclasses import dataclass

@dataclass
class Credentials():
    userame:str = ""
    password:str = ""
    port:int = 0
    hostname:str = ""
    usefolder:str = ""

def downloadEdsFiles(eng, outputsFolder, currentTorqueSpeed, withstand):
    #Connection parameters
    credentials = getLoginCredentials(eng)

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

    
    mainFilename = '%T.MAIN'
    withstandFileName = '%T.WTHSTND'
    pathToSaveMainFile = outputsFolder + '\\' + mainFilename
    pathToSaveWithstandFile = outputsFolder + '\\' + withstandFileName

    if currentTorqueSpeed == 1:
        with open(pathToSaveMainFile, 'wb') as file:
            returnCode = ftp.retrbinary(f"RETR {mainFilename}", file.write)

    if withstand == 1:
        with open(pathToSaveWithstandFile, 'wb') as file:
            returnCode = ftp.retrbinary(f"RETR {withstandFileName}", file.write)
    
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
        
    elif eng == 'PMV':
        credentials.userame = 'pmv'
        credentials.password = 'viool'

    elif eng == 'DM':
        credentials.userame = 'mkm'
        credentials.password = 'Keletso01'
    
    elif eng == 'PR':
        credentials.userame = 'ra'
        credentials.password = 'skud'
    
    elif eng == 'DW':
        credentials.userame = 'kg'
        credentials.password = 'kgodyn'
    
    elif eng == 'JN':
        credentials.userame = 'kg'
        credentials.password = 'kgodyn'

    return credentials


