import win32com.client, os
from ftplib import FTP
FTP_ROOT = 'ftp.bgc-jena.mpg.de'
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"

def GetFTPFile(ftpFullFilename): #gets an ftp file from the server
    '''retrieves an ftp file from a server'''
    ftpRelativeFilename = ftpFullFilename[ftpFullFilename.find("/"):]
    filename = os.path.basename(ftpRelativeFilename)
    localFilename = INPUT_ZIPS + filename
    if os.path.exists(localFilename):
        print "Already exists - skipping" 
    else:
#         if "meteo" in ftpFullFilename:
#             print "Big climate NetCDF file - skipping for now"
#             return
        try:
            print "Getting file " +  filename
            ftp.retrbinary('RETR %s' % ftpRelativeFilename, open(localFilename, 'wb').write)
        except (Exception) as e:
            print e
            pass
        print "\t\tSucceeded"
    return 

ftp = FTP(FTP_ROOT)
ftp.login()
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
# queryDef = db.CreateQueryDef("", "select distinct fullPath from [required files] where model<>'Climate'")
queryDef = db.CreateQueryDef("", "select distinct fullPath from [required files] where fullpath like '*daily.pr.africa.nc.gz*'") # rainfall only
table = queryDef.OpenRecordset()
total = table.RecordCount
counter = 1
while not table.EOF:
    ftpFullFilename = str(table.fullPath)
    GetFTPFile(ftpFullFilename)
    table.MoveNext()
    counter = counter + 1 
    print str(counter) + " out of " + str(total)
db.Close()
ftp.quit()
ftp.close()