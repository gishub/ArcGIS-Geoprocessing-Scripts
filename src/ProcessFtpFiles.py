import win32com.client, os, subprocess
from ftplib import FTP
PYTHON_PATH = 'C:/Python27/ArcGIS10.2/python.exe'
WORKER_SCRIPT = 'D:/Users/andrewcottam/Documents/GitHub/ArcGIS-Geoprocessing-Scripts/src/ProcessNetCDFFiles.py'
FTP_ROOT = 'ftp.bgc-jena.mpg.de'
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"
START_TEXT = "Extracting  "
END_TEXT = "Everything"

def GetFTPFile(ftpFullFilename):
    '''retrieves an ftp file from a server'''
    ftpRelativeFilename = ftpFullFilename[ftpFullFilename.find("/"):]
    print "\n================================================================================================================================="
    print "Getting file:\t'.." + ftpFullFilename[19:] + "'"
    filename = os.path.basename(ftpRelativeFilename)
    localFilename = INPUT_ZIPS + filename
    if os.path.exists(localFilename):
        print "\t\tAlready exists - skipping" 
    else:
        try:
            ftp.retrbinary('RETR %s' % ftpRelativeFilename, open(localFilename, 'wb').write)
        except (Exception) as e:
            print e
            pass
            
        print "\t\tSucceeded"
    return localFilename

def UnzipGZFile(gzfile, outputfolder, deleteZipfile):
    '''unzips a gz file using 7zip'''
    print "Unzipping:\t'" + gzfile + "'.."
    p = subprocess.Popen('7z e "' + gzfile + '" -o"' + outputfolder + '" -aos', stdout=subprocess.PIPE)
    result = p.communicate()[0]
    pos = result.find(START_TEXT)
    if pos > -1:
        extractedFilename = result[pos + len(START_TEXT):result.find(END_TEXT) - 4]
        extractedFilename = outputfolder + os.path.basename(extractedFilename)  # to force the file name to have / slashes in its path
        print "\t\tSucceeded"
    else:
        extractedFilename = outputfolder + os.path.basename(gzfile[1:-3])
        print "\t\tAlready exists - skipping" 
    if deleteZipfile:
        print "Deleting:\t'" + gzfile + "'"
        os.remove(gzfile)
        print "\t\tSucceeded"
    if os.path.exists(extractedFilename):
        return extractedFilename
    else:
        print "\t\tArchive name does not match zip name - trying to rename"
        return extractedFilename.replace("_qmbc_", "_somd_")

ftp = FTP(FTP_ROOT)
ftp.login()
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
# table = db.TableDefs("required files lpjg").OpenRecordset()
# queryDef = db.CreateQueryDef("", 'select distinct fullPath, frequency from [required files] where model<>"climate" and frequency="lta"')
queryDef = db.CreateQueryDef("", "select distinct fullPath, frequency from [required files] where model<>'climate' and frequency='lta' and fullpath like '*harea*'")
table = queryDef.OpenRecordset()
r = queryDef.openrecordset()
counter = 1
while not table.EOF:
    ftpFullFilename = str(table.fullPath)
    required_frequency = str(table.frequency)
    gzfile = GetFTPFile(ftpFullFilename)
    file = UnzipGZFile(gzfile, INPUT_DATA, False)
    p = subprocess.Popen([PYTHON_PATH, WORKER_SCRIPT , file, "lta20"])
    p.wait()
    p.kill()
    if os.path.exists(file):
        os.remove(file)
#     if os.path.exists(gzfile):
#         os.remove(gzfile)
    table.MoveNext()
    counter = counter + 1 
db.Close()
ftp.quit()
ftp.close()
