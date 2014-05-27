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
    p.wait()
    p.kill()
    print "\t\tSucceeded"

if os.path.exists(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log"):
    os.remove(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log")  # remove the log file
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
# queryDef = db.CreateQueryDef("", "select * from DownloadedZipFiles")
queryDef = db.CreateQueryDef("", "select * from DownloadedZipFiles where fullpath like '*somds.wfdei.cmip5.rcp85.CanESM2.daily.pr.africa.nc*'")
# queryDef = db.CreateQueryDef("", "select * from DownloadedZipFiles where filename ='ClimAf_1_1960-2100_lpjg_can_wfdei_qmbc_B1_etotx_sea_teco_ir.nc.gz'")
table = queryDef.OpenRecordset()
counter = 1
while not table.EOF:
    gzfile = str(table.fullpath)
    archivename = str(table.archivename)
    UnzipGZFile(gzfile, archivename)
#     archivename="ClimAf_1_1961_2099_lpjm_mir_wfdei_qmbc_B1_petxx_sea_teco_ir.nc"
#     call the subprocess to process the data - passing the path to the netcdf file, the frequency, e.g. day, month, year, lta+num, how to summarise the data, e.g. mean, and whether to zipped the summarised results and delete the intermediate date
    p = subprocess.Popen([PYTHON_PATH, WORKER_SCRIPT , INPUT_DATA + archivename, "lta20", "mean","false"])
#     p = subprocess.Popen([PYTHON_PATH, WORKER_SCRIPT , INPUT_DATA + archivename, "lta2", "sum", "false"])  # for cumulative precipitation
    p.wait()
    p.kill()
#     if os.path.exists(INPUT_DATA + archivename):
#         os.remove(INPUT_DATA + archivename)
    table.MoveNext()
    counter = counter + 1
    break
db.Close()
