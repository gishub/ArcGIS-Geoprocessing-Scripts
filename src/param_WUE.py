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

def GetVariableName(variablenames, dataset):
    for v in variablenames:
        if v in dataset.variables.keys():
            return v
    raise FAOException("Dataset variable name cannot be found. Tried using " + ",".join([n for n in variablenames]))

def CreateNetCDF(dataset1, dataset2, parameter):
    numpy.seterr(all='ignore')
#     get the name of the output netcdf file
    outputNetCDF = INPUT_DATA + dataset1.replace(parameter['firstDatasetKeyword'], "_" + parameter['name'] + "_sea_")
#     get the 2 input netcdf files and load them into memory
    data1 = Dataset(INPUT_DATA + dataset1)
    data2 = Dataset(INPUT_DATA + dataset2)
    try:
        variablename1 = GetVariableName(parameter['variablenames1'], data1)
        variablename2 = GetVariableName(parameter['variablenames2'], data2)
        dataset1Lon = GetLongitudeVariableName(data1)
        dataset1Lat = GetLatitudeVariableName(data1)
        new_data = numpy.divide(data1.variables[variablename1][:, :, :], data2.variables[variablename2][:, :, :])    
        outputData = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC')    
        outputData.createDimension(u'lon', data1.variables[dataset1Lon].size)
        outputData.createDimension(u'lat', data1.variables[dataset1Lat].size) 
        outputData.createDimension(u'time', data1.variables['time'].size)
        longitudes = outputData.createVariable(u'lon', 'f4', ('lon',))
        latitudes = outputData.createVariable(u'lat', 'f4', ('lat',))
        times = outputData.createVariable(u'time', 'f8', ('time',))
        outputvariable = outputData.createVariable(u'wue', 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
        longitudes[:] = data1.variables[dataset1Lon][:] 
        latitudes[:] = data1.variables[dataset1Lat][:]
        times[:] = data1.variables['time'][:] 
        outputvariable[:, :, :] = new_data[:, :, :]
        outputData.close() 
    except (MemoryError):
        logging.error("MemoryError while creating " + outputNetCDF)
        return ""
    except (FAOException) as e:
        logging.error(e.message)
        print e.message
        return ""
    finally:
        data1.close()
        data2.close()
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

parameters = [
    {"name":"wuexx", "firstDatasetKeyword" :"_yield_sea_", "secondDatasetKeyword" : "_etotx_sea_","variablenames1":["yield","harvest"],"variablenames2":["AET","et"]}
]    
parameter=parameters[0]
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE (((DownloadedZipFiles.filename) Like '*" + parameter['firstDatasetKeyword'] + "*'));")
# queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE filename='ClimAf_1_1961_2099_lpjm_can_wfdei_qmbc_B1_yield_sea_teco_ir.nc.gz';")
r = queryDef.OpenRecordset()
total = r.RecordCount
counter = 1
logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
while not r.EOF:
    print "Creating NetCDF files for parameter " + parameter['name'] + " (" + str(counter) + "/" + str(total) + ")\n================================================================="
    gzfile1 = str(r.fullpath)
    gzfile2 = gzfile1.replace(parameter['firstDatasetKeyword'], parameter['secondDatasetKeyword'])
    archivename1 = str(r.archivename)
    if (os.path.exists(INPUT_ZIPS + archivename1.replace(parameter['firstDatasetKeyword'][1:6], parameter['name']) + ".gz")):
        print "Output zipped NetCDF file already exists"
    else:
        rightpart = archivename1[archivename1.find(parameter['firstDatasetKeyword'][0:7]) - 3:].replace(parameter['firstDatasetKeyword'], parameter['secondDatasetKeyword'])  # archive name may not be the same as yield one - e.g. somd
        leftbit = archivename1[:archivename1.find("_wfdei_")]
        sql = "Select archivename from downloadedzipfiles where filename like '*" + parameter['secondDatasetKeyword'] + "*' and filename like '*" + rightpart + "*' and filename like '*" + leftbit + "*';"
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
                netcdfFile = CreateNetCDF(archivename1, archivename2,  parameter)
                if netcdfFile:
                    print "Created " + netcdfFile + "\nZipping file"
                    zippedNetCDF = zipUpNetCDFFile(netcdfFile)
                    print "Finished\n\n"
                    os.remove(netcdfFile)
                else:
                    print "NetCDF File not created"
            except (IOError):
                logging.error("Error creating NetCDF file for " + parameter['name'] + " parameter. Required gz file " + gzfile2 + " not found")
                print "Error creating NetCDF file for " + parameter['name'] + " parameter. Required gz file " + gzfile2 + " not found"
            except (MemoryError):
                logging.error("MemoryError creating NetCDF file for " + gzfile2)
                print "MemoryError creating NetCDF file for " + gzfile2 
            if os.path.exists(INPUT_DATA + archivename2):
                os.remove(INPUT_DATA + archivename2)
        else:
            logging.error("Error creating NetCDF file for " + parameter['name'] + " parameter. Required gz file " + gzfile2 + " not found")
            print "Error creating NetCDF file for " + parameter['name'] + " parameter. Required gz file " + gzfile2 + " not found"
        if os.path.exists(INPUT_DATA + archivename1):
            os.remove(INPUT_DATA + archivename1)
    r.MoveNext()
    counter = counter + 1
db.Close()

