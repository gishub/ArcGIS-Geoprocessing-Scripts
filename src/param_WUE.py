import win32com.client, subprocess, os, numpy, netCDF4, gzip, logging
from netCDF4 import Dataset
PYTHON_PATH = 'C:/Python27/ArcGIS10.2/python.exe'
WORKER_SCRIPT = 'D:/Users/andrewcottam/Documents/GitHub/ArcGIS-Geoprocessing-Scripts/src/ProcessNetCDFFiles.py'
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"

class FAOException(Exception):
    pass

def UnzipGZFile(gzfile, archivename):
    '''unzips a gz file using 7zip'''
    if os.path.exists(INPUT_DATA + archivename):
        print "Already exists - skipping" 
        return
    p = subprocess.Popen('7z e "' + gzfile + '" -o"' + INPUT_DATA + '" -aos', stdout=subprocess.PIPE)
    result = p.communicate()[0]
    if "cannot find" in result:
        raise IOError("Cannot find file " + gzfile)
    p.wait()
    p.kill()

def MatchVariableNameInDataset(possiblenames, dataset):
    for v in dataset.variables.keys():
        if v in possiblenames:
            return v
    raise FAOException("Dataset variable name cannot be found. Tried using " + ",".join([n for n in possiblenames]))

def GetLongitudeVariableName(dataset):
    if "lon" in dataset.variables.keys():
        return "lon"
    else:
        return "longitude"

def GetLatitudeVariableName(dataset):
    if "lat" in dataset.variables.keys():
        return "lat"
    else:
        return "latitude"

def GetVariableNameForParameter(parameter, dataset):
    if parameter == 'yield':
        return MatchVariableNameInDataset(["yield", "harvest"], dataset)
    elif parameter == "etotx":
        return MatchVariableNameInDataset(["AET", "et"], dataset)

def CreateNetCDF(yieldNetCDFFile, etotNetCDFFile):
    numpy.seterr(all='ignore')
    outputNetCDF = INPUT_DATA + yieldNetCDFFile.replace("_yield_sea_", "_wuexx_sea_")
    yield_data = Dataset(INPUT_DATA + yieldNetCDFFile)
    etot_data = Dataset(INPUT_DATA + etotNetCDFFile)
    try:
        yieldVariablename = GetVariableNameForParameter("yield", yield_data)
        etotVariablename = GetVariableNameForParameter("etotx", etot_data)
        yieldlon=GetLongitudeVariableName(yield_data)
        yieldlat=GetLatitudeVariableName(yield_data)
        new_data = numpy.divide(yield_data.variables[yieldVariablename][:, :, :], etot_data.variables[etotVariablename][:, :, :])    
        wue_data = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC')    
        wue_data.createDimension(u'lon', yield_data.variables[yieldlon].size)
        wue_data.createDimension(u'lat', yield_data.variables[yieldlat].size) 
        wue_data.createDimension(u'time', yield_data.variables['time'].size)
        longitudes = wue_data.createVariable(u'lon', 'f4', ('lon',))
        latitudes = wue_data.createVariable(u'lat', 'f4', ('lat',))
        times = wue_data.createVariable(u'time', 'f8', ('time',))
        wue = wue_data.createVariable(u'wue', 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
        longitudes[:] = yield_data.variables[yieldlon][:] 
        latitudes[:] = yield_data.variables[yieldlat][:]
        times[:] = yield_data.variables['time'][:] 
        wue[:, :, :] = new_data[:, :, :]
        wue_data.close() 
    except (MemoryError):
        logging.error("MemoryError while creating " + outputNetCDF)
        return ""
    except (FAOException) as e:
        logging.error(e.message)
        print e.message
        return ""
    finally:
        yield_data.close()
        etot_data.close()
    return outputNetCDF   

def zipUpNetCDFFile(netcdfFile):
    filename = os.path.basename(netcdfFile)
    zipFilename = INPUT_ZIPS + filename + ".gz"
    f_in = open(netcdfFile, 'rb')
    f_out = gzip.open(zipFilename, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    return zipFilename

engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE (((DownloadedZipFiles.filename) Like '*_yield_sea_*'));")
# queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE filename='ClimAf_1_1961_2099_lpjm_can_wfdei_qmbc_B1_yield_sea_teco_ir.nc.gz';")
r = queryDef.OpenRecordset()
total = r.RecordCount
counter = 1
logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
while not r.EOF:
    print "Creating NetCDF files for wue parameter (" + str(counter) + "/" + str(total) + ")\n================================================================="
    gzfile1 = str(r.fullpath)
    gzfile2 = gzfile1.replace("_yield_sea_", "_etotx_sea_")
    archivename1 = str(r.archivename)
    if (os.path.exists(INPUT_ZIPS + archivename1.replace("yield", "wuexx") + ".gz")):
        print "Output zipped NetCDF file already exists"
    else:
        rightpart = archivename1[archivename1.find("_yield_") - 3:].replace("_yield_sea_", "_etotx_sea_")  # archive name may not be the same as yield one - e.g. somd
        leftbit = archivename1[:archivename1.find("_wfdei_")]
        sql = "Select archivename from downloadedzipfiles where filename like '*_etotx_sea_*' and filename like '*" + rightpart + "*' and filename like '*" + leftbit + "*';"
        querydef2 = db.CreateQueryDef("", sql)
        q2 = querydef2.OpenRecordset()
        if q2.EOF == False:
            archivename2 = str(q2.archivename)
            try:
                print "Unzipping " + gzfile1
                UnzipGZFile(gzfile1, archivename1)
                print "Unzipping " + gzfile2
                UnzipGZFile(gzfile2, archivename2)
                print "Creating the Netcdf file"
                netcdfFile = CreateNetCDF(archivename1, archivename2)
                if netcdfFile:
                    print "Created " + netcdfFile + "\nZipping file"
                    zippedNetCDF = zipUpNetCDFFile(netcdfFile)
                    print "Finished\n\n"
                    os.remove(netcdfFile)
                else:
                    print "NetCDF File not created"
            except (IOError):
                logging.error("Error creating NetCDF file for WUE parameter. Required gz file " + gzfile2 + " not found")
                print "Error creating NetCDF file for WUE parameter. Required gz file " + gzfile2 + " not found"
            except (MemoryError):
                logging.error("MemoryError creating NetCDF file for " + gzfile2)
                print "MemoryError creating NetCDF file for " + gzfile2 
            if os.path.exists(INPUT_DATA + archivename2):
                os.remove(INPUT_DATA + archivename2)
        else:
            logging.error("Error creating NetCDF file for WUE parameter. Required gz file " + gzfile2 + " not found")
            print "Error creating NetCDF file for WUE parameter. Required gz file " + gzfile2 + " not found"
        if os.path.exists(INPUT_DATA + archivename1):
            os.remove(INPUT_DATA + archivename1)
    r.MoveNext()
    counter = counter + 1
        
db.Close()

