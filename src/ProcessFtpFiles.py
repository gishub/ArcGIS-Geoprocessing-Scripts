import win32com.client, os
from ftplib import FTP
FTP_ROOT = 'ftp.bgc-jena.mpg.de'
UNZIP_FOLDER = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"

def GetFile(ftpRelativeFilename):
    filename = os.path.basename(ftpRelativeFilename)
    localFilename = UNZIP_FOLDER + filename
    ftp.retrbinary('RETR %s' % ftpRelativeFilename, open(localFilename, 'wb').write)
    return localFilename
    
ftp = FTP(FTP_ROOT)
ftp.login()
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
table = db.TableDefs("required files lpjg").OpenRecordset()
counter = 1
while not table.EOF:
    ftpFullFilename = str(table.fullPath)
    ftpRelativeFilename = ftpFullFilename[ftpFullFilename.find("/"):]
    filename = GetFile(ftpRelativeFilename)
    print "'" + os.path.basename(filename) + "' copied from '" + ftpFullFilename + "'"
    table.MoveNext()
    break 
db.Close()
