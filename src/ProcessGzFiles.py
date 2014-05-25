import win32com.client, os, subprocess
PYTHON_PATH = 'C:/Python27/ArcGIS10.2/python.exe'
WORKER_SCRIPT = 'D:/Users/andrewcottam/Documents/GitHub/ArcGIS-Geoprocessing-Scripts/src/ProcessNetCDFFiles.py'
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"

def UnzipGZFile(gzfile, archivename):
    '''unzips a gz file using 7zip'''
    print "Unzipping:\t'" + gzfile + "'.."
    if os.path.exists(INPUT_DATA + archivename):
        print "\t\tAlready exists - skipping" 
        return
    p = subprocess.Popen('7z e "' + gzfile + '" -o"' + INPUT_DATA + '" -aos', stdout=subprocess.PIPE)
    print "\t\tSucceeded"

if os.path.exists(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log"):
    os.remove(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log")  # remove the log file
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
queryDef = db.CreateQueryDef("", "select * from DownloadedZipFiles")
table = queryDef.OpenRecordset()
counter = 1
while not table.EOF:
    gzfile = str(table.fullpath)
    archivename = str(table.archivename)
    UnzipGZFile(gzfile, archivename)
    p = subprocess.Popen([PYTHON_PATH, WORKER_SCRIPT , INPUT_DATA + archivename, "lta20", "false"])
    p.wait()
    p.kill()
    if os.path.exists(INPUT_DATA + archivename):
        os.remove(INPUT_DATA + archivename)
    table.MoveNext()
    counter = counter + 1
    break
db.Close()
