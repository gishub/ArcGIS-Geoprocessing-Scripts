import win32com.client, subprocess, os, numpy, netCDF4, gzip, logging,datetime
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
    raise FAOException("Variable names: " + ",".join([n for n in variablenames]) + " do not match those available: " + ",".join([k for k in dataset.variables.keys()]))

def CreateNetCDF(dataset1, dataset2, parameter):
    numpy.seterr(all='ignore')
#     get the name of the output netcdf file
    outputNetCDF = INPUT_DATA + dataset1.replace(parameter['firstDatasetKeyword'], "_" + parameter['name'] + "_sea_")
#     get the 2 input netcdf files and load them into memory
    data1 = Dataset(INPUT_DATA + dataset1)
    data2 = Dataset(INPUT_DATA + dataset2)
    try:
#         get the variable name for the first dataset
        variablename1 = GetVariableName(parameter['variablenames1'], data1)
#         get the variable name for the second dataset
        variablename2 = GetVariableName(parameter['variablenames2'], data2)
#         get the name of the lat and lon variables for the first dataset - we will use the dimensions and data from the first dataset to create our netcdf
        dataset1Lon = GetLongitudeVariableName(data1)
        dataset1Lat = GetLatitudeVariableName(data1)
#         get the new derived data as a numpy array -this is the main calculation
        if parameter['name'] == "wuexx":
            new_data = numpy.divide(data1.variables[variablename1][:, :, :], data2.variables[variablename2][:, :, :])   
        if parameter['name'] == "wrsix":
            new_data = numpy.divide(data1.variables[variablename1][:, :, :], data2.variables[variablename2][:, :, :]) * 1000  
#         create the new netcdf output file
        outputData = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC') 
        outputData.history= str(datetime.datetime.now()) + ". Created from the input NetCDF files: "
#         create the new dimensions in the netcdf file 
        outputData.createDimension(u'lon', data1.variables[dataset1Lon].size)
        outputData.createDimension(u'lat', data1.variables[dataset1Lat].size) 
        outputData.createDimension(u'time', data1.variables['time'].size)
#         create the new variables in the netcdf file
        longitudes = outputData.createVariable(u'lon', 'f4', ('lon',))
        latitudes = outputData.createVariable(u'lat', 'f4', ('lat',))
        times = outputData.createVariable(u'time', 'f8', ('time',))
        outputvariable = outputData.createVariable(parameter['outputvariablename'], 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
#         populate the lat/lon/time values from the input dataset
        longitudes[:] = data1.variables[dataset1Lon][:] 
        latitudes[:] = data1.variables[dataset1Lat][:]
        times[:] = data1.variables['time'][:] 
#         populate the output variable
        outputvariable[:, :, :] = new_data[:, :, :]
        outputData.close() 
    except (MemoryError):
        logging.error("MemoryError while creating " + outputNetCDF)
        print "MemoryError while creating " + outputNetCDF
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

def GetMatchingFiles(keyword):
    '''searches for a record in the table which contains the passed keyword'''
    files = []
    queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE (((DownloadedZipFiles.filename) Like '*" + keyword + "*'));")
    r = queryDef.OpenRecordset()
    while not r.EOF:
        files.append({"fullpath":str(r.fullpath), "archivename":str(r.archivename)})
        r.MoveNext()
    return files

def GetFilesToProcess(parameter):
    filesToProcess = []
    zipfiles1 = GetMatchingFiles(parameter['firstDatasetKeyword'])
    if "_ann_" in parameter['firstDatasetKeyword']:
        if "_ann_" in parameter['secondDatasetKeyword']:
            zipfiles2 = GetMatchingFiles(parameter['firstDatasetKeyword'])
            allfiles = GetMatchingFiles2(zipfiles1)
        else:
            zipfiles2 = GetMatchingFiles(parameter['secondDatasetKeyword'])
    else:
        for zipfile1 in zipfiles1:
            zipfile2 = zipfile1["fullpath"].replace(parameter['firstDatasetKeyword'], parameter['secondDatasetKeyword'])
            archivename1 = zipfile1["archivename"]
            rightpart = archivename1[archivename1.find(parameter['firstDatasetKeyword'][0:7]) - 3:].replace(parameter['firstDatasetKeyword'], parameter['secondDatasetKeyword'])  # archive name may not be the same as yield one - e.g. somd
            leftbit = archivename1[:archivename1.find("_wfdei_")]
            sql = "Select archivename from downloadedzipfiles where filename like '*" + parameter['secondDatasetKeyword'] + "*' and filename like '*" + rightpart + "*' and filename like '*" + leftbit + "*';"
            querydef2 = db.CreateQueryDef("", sql)
            q2 = querydef2.OpenRecordset()
            if q2.EOF == False:
                archivename2 = str(q2.archivename)
            else:
                archivename2 = ""
            filesToProcess.append([zipfile1["fullpath"], archivename1, zipfile2, archivename2])
    return filesToProcess
        
def CreateNetCDFs(parameter):
    counter = 1
    filesToProcess = GetFilesToProcess(parameter)
    total = len(filesToProcess)
    for file in filesToProcess:
        print "\nCreating NetCDF files for parameter " + parameter['name'] + " (" + str(counter) + "/" + str(total) + ")\n================================================================="
        gzfile1 = file[0]
        archivename1 = file[1]
        gzfile2 = file[2]
        archivename2 = file[3]
        if archivename2:
            if (os.path.exists(INPUT_ZIPS + archivename1.replace(parameter['firstDatasetKeyword'][1:6], parameter['name']) + ".gz")):
                print "Output zipped NetCDF file already exists"
            else:
                try:
                    print "Unzipping " + os.path.basename(gzfile1)
                    UnzipGZFile(gzfile1, archivename1)
                    print "Unzipping " + os.path.basename(gzfile2)
                    UnzipGZFile(gzfile2, archivename2)
                    print "Creating the Netcdf file"
                    netcdfFile = CreateNetCDF(archivename1, archivename2, parameter)
                    if netcdfFile:
                        print "Created " + os.path.basename(netcdfFile) + "\nZipping file"
                        zippedNetCDF = zipUpNetCDFFile(netcdfFile)
                        print "Created " + os.path.basename(zippedNetCDF)
                        os.remove(netcdfFile)
                    else:
                        print "NetCDF File not created"
                except (IOError):
                    logging.error(gzfile2 + " not found")
                    print gzfile2 + " not found"
                except (MemoryError):
                    logging.error("MemoryError creating NetCDF file for " + gzfile2)
                    print "MemoryError creating NetCDF file for " + gzfile2 
                if os.path.exists(INPUT_DATA + archivename2):
                    os.remove(INPUT_DATA + archivename2)
                if os.path.exists(INPUT_DATA + archivename1):
                    os.remove(INPUT_DATA + archivename1)
        else:
            print "No corresponding file found for " + archivename1
        counter = counter + 1
    
parameters = [
# {"name":"wuexx", "firstDatasetKeyword" :"_yield_sea_", "secondDatasetKeyword" : "_etotx_sea_", "variablenames1":["yield", "harvest"], "variablenames2":["AET", "et"],"outputvariablename":"wue"},
{"name":"wrsix", "firstDatasetKeyword" :"_etotx_sea_", "secondDatasetKeyword" : "_petxx_sea_", "variablenames1":["AET", "et"], "variablenames2":["PET", "pet"],"outputvariablename":"wrsi"},
# {"name":"aixxx", "firstDatasetKeyword" :"_precx_ann_", "secondDatasetKeyword" : "_petxx_sea_", "variablenames1":["pre"], "variablenames2":["PET", "pet"],"outputvariablename":"ai"}
]   
logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
for parameter in parameters:
    CreateNetCDFs(parameter)
db.Close()

