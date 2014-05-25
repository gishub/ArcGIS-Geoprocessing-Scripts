import win32com.client, subprocess, os, numpy, netCDF4,gzip
from netCDF4 import Dataset
PYTHON_PATH = 'C:/Python27/ArcGIS10.2/python.exe'
WORKER_SCRIPT = 'D:/Users/andrewcottam/Documents/GitHub/ArcGIS-Geoprocessing-Scripts/src/ProcessNetCDFFiles.py'
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"

def UnzipGZFile(gzfile, archivename):
    '''unzips a gz file using 7zip'''
    if os.path.exists(INPUT_DATA + archivename):
        print "Already exists - skipping" 
        return
    p = subprocess.Popen('7z e "' + gzfile + '" -o"' + INPUT_DATA + '" -aos', stdout=subprocess.PIPE)
    result = p.communicate()[0]
    if "cannot find" in result:
        raise Exception("Cannot find file " + gzfile)

def CreateNetCDF(yieldNetCDFFile, etotNetCDFFile):
    numpy.seterr(all='ignore')
    yield_data = Dataset(INPUT_DATA + yieldNetCDFFile)
    etot_data = Dataset(INPUT_DATA + etotNetCDFFile)
    outputNetCDF = INPUT_DATA + yieldNetCDFFile.replace("_yield_sea_", "_wuexx_sea_")
    new_data = numpy.divide(yield_data.variables['yield'][:, :, :], etot_data.variables['AET'][:, :, :])    
    wue_data = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC')    
    wue_data.createDimension(u'lon', yield_data.variables['lon'].size)
    wue_data.createDimension(u'lat', yield_data.variables['lat'].size) 
    wue_data.createDimension(u'time', yield_data.variables['time'].size)
    longitudes = wue_data.createVariable(u'lon', 'f4', ('lon',))
    latitudes = wue_data.createVariable(u'lat', 'f4', ('lat',))
    times = wue_data.createVariable(u'time', 'f8', ('time',))
    wue = wue_data.createVariable(u'wue', 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
    longitudes[:] = yield_data.variables['lon'][:] 
    latitudes[:] = yield_data.variables['lat'][:]
    times[:] = yield_data.variables['time'][:] 
    wue[:, :, :] = new_data[:, :, :]                        
    wue_data.close() 
    return outputNetCDF   

def zipUpNetCDFFile(netcdfFile):
    filename=os.path.basename(netcdfFile)
    zipFilename = INPUT_ZIPS + filename + ".gz"
    f_in = open(netcdfFile, 'rb')
    f_out = gzip.open(zipFilename, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    return zipFilename

engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
queryDef = db.CreateQueryDef("", "SELECT * FROM DownloadedZipFiles WHERE (((DownloadedZipFiles.filename) Like '*_yield_sea_*'));")
r = queryDef.OpenRecordset()
counter = 0
while not r.EOF:
    print "Creating NetCDF files for wue parameter\n================================================================="
    gzfile1 = str(r.fullpath)
    gzfile2 = gzfile1.replace("_yield_sea_", "_etotx_sea_")
    archivename1 = str(r.archivename)
    archivename2 = archivename1.replace("_yield_sea_", "_etotx_sea_")
    print "Unzipping " + gzfile1
    UnzipGZFile(gzfile1, archivename1)
    print "Unzipping " + gzfile1
    UnzipGZFile(gzfile2, archivename2)
    print "Creating the Netcdf file"
    netcdfFile = CreateNetCDF(archivename1, archivename2)
    print netcdfFile + " file created\nZipping file\n"
    zippedNetCDF = zipUpNetCDFFile(netcdfFile)
    print "Finished\n\n"
    os.remove(netcdfFile)
    r.MoveNext()
    counter = counter + 1
db.Close()

