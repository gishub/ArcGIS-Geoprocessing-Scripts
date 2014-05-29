import win32com.client, os, subprocess, netCDF4, gzip, datetime
from netCDF4 import Dataset
DATABASE_PATH = "D:/Users/andrewcottam/Documents/fao_ftp_files.accdb"
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"
OUTPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Data/"

class FAOException(Exception):
    pass

def UnzipGZFile(gzfile, archivename):
    '''unzips a gz file using 7zip'''
    if os.path.exists(INPUT_DATA + archivename):
        print "Zip file already exists - skipping" 
    else:
        print "Unzipping " + os.path.basename(gzfile)
        p = subprocess.Popen('7z e "' + gzfile + '" -o"' + INPUT_DATA + '" -aos', stdout=subprocess.PIPE)
        result = p.communicate()[0]
        if "cannot find" in result:
            raise IOError("Cannot find file " + gzfile)
        p.wait()
        print "Unzipped " + archivename 
        p.kill()
    return INPUT_DATA + archivename

def ZipFile(netcdfFile):
    zipFilename = GetNetCDFZipOutputFilename(netcdfFile)
    f_in = open(netcdfFile, 'rb')
    f_out = gzip.open(zipFilename, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    return zipFilename

def GetNetCDFOutputFilename(templateStr, searchStr, replaceStr):  # creates a NetCDF output filename 
    netcdfFile = templateStr.replace(searchStr, replaceStr)  
    return OUTPUT_DATA + netcdfFile

def GetNetCDFZipOutputFilename(netdfFile):  # creates a NetCDF output filename - returns an empty string if the file already exists
    netcdfFileZip = INPUT_ZIPS + os.path.basename(netdfFile) + ".gz"
    if os.path.exists(netcdfFileZip):
        return ""
    else:
        return netcdfFileZip

def GetPeriodFromFilename(f):
    filename = os.path.basename(f)
    if (filename[:6] == "ClimAf"):
        return (filename[9:13], filename[14:18])
    else:
        return ("1960", "2100")  # default period is 1960-2100

def GetMatchingGZFiles(f):
    engine = win32com.client.Dispatch('DAO.DBEngine.120')
    db = engine.OpenDatabase(DATABASE_PATH)
    queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename, ftpurl FROM DownloadedZipFiles WHERE DownloadedZipFiles.filename Like '*" + f + "*';")
#     print queryDef.Sql
    r = queryDef.OpenRecordset()
    records = []
    while not r.EOF:
        records.append([str(r.fields[i]) for i in range(r.fields.count)])
        r.MoveNext()
    db.Close()
    return records

def GetCropGroupsAndFilenames(param):
    engine = win32com.client.Dispatch('DAO.DBEngine.120')
    db = engine.OpenDatabase(DATABASE_PATH)
    queryDef = db.QueryDefs("crop groups and filenames " + param)
    r = queryDef.OpenRecordset()
    records = []
    while not r.EOF:
        records.append([str(r.fields[i]) for i in range(r.fields.count)])
        r.MoveNext()
    db.Close()
    return records

def GetFilesForGroup(likeclauses):
    engine = win32com.client.Dispatch('DAO.DBEngine.120')
    db = engine.OpenDatabase(DATABASE_PATH)
    sqlclausess = " ".join(["OR filename LIKE '*" + s + "*'" for s in likeclauses])[3:]
    queryDef = db.CreateQueryDef("", "SELECT DISTINCT DownloadedZipFiles.fullpath, DownloadedZipFiles.archivename FROM DownloadedZipFiles WHERE " + sqlclausess)
    r = queryDef.OpenRecordset()
    records = []
    while not r.EOF:
        records.append([str(r.fields[i]) for i in range(r.fields.count)])
        r.MoveNext()
    db.Close()
    return records
 
def GetCorrespondingFile(f, searchStr, replaceStr):
    engine = win32com.client.Dispatch('DAO.DBEngine.120')
    db = engine.OpenDatabase(DATABASE_PATH)
    rightpart = f[f.find(searchStr[0:7]) - 3:].replace(searchStr, replaceStr)  # archive name may not be the same as yield one - e.g. somd
    leftbit = f[:f.find("_wfdei_")]
    sql = "Select archivename from downloadedzipfiles where filename like '*" + replaceStr + "*' and filename like '*" + rightpart + "*' and filename like '*" + leftbit + "*';"
    querydef = db.CreateQueryDef("", sql)
    r = querydef.OpenRecordset()
    if not r.EOF:
        return str(r.archivename)
    else:
        raise FAOException("No corresponding files found")

def GetNetCDFData(dataset,variableName): #gets the data from the array ignoring any single dimension entries
    if dataset.variables[variableName].ndim>3:
        return dataset.variables[variableName][:].squeeze()
    else:
        return dataset.variables[variableName][:,:,:]

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
def GetVariableName(dataset):
    for varname in dataset.variables.keys():
        if varname not in ["lon", "lat", "longitude", "latitude", "time", "lev"]:
            return varname
    raise Exception("Variable name not found for dataset")
        
def CreateNetCDFFile(source, data, outputNetCDF, variablename, long_name, unit, ftpurl, expression, time):
    dataset = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC')
    dataset.history = "File created from NetCDF file: " + ftpurl + " by Andrew Cottam using expression " + expression + " on " + str(datetime.datetime.now()) 
    lonName = GetLongitudeVariableName(source)
    latName = GetLatitudeVariableName(source)
    dataset.createDimension(u'lon', source.variables[lonName].size)
    dataset.createDimension(u'lat', source.variables[latName].size) 
    dataset.createDimension(u'time', data.shape[0])
    longitudes = dataset.createVariable(u'lon', 'f4', ('lon',))
    longitudes[:] = source.variables[lonName][:] 
    longitudes.standard_name = "longitude"
    longitudes.long_name = "longitude"
    longitudes.units = "degrees_east"
    longitudes.axis = "X"
    latitudes = dataset.createVariable(u'lat', 'f4', ('lat',))
    latitudes[:] = source.variables[latName][:]
    latitudes.standard_name = "latitude"
    latitudes.long_name = "latitude"
    latitudes.units = "degrees_north"
    latitudes.axis = "Y"
    times = dataset.createVariable(u'time', 'f8', ('time',))
    if times.size == 1:
        times[:] = [2000]  # assume year 2000
    else:
        times[:] = source.variables['time'][:] 
    times.standard_name = "time"
    times.units = "year as %Y.%f"
    times.period = time
    times.calendar = "proleptic_gregorian"
    outputvariable = dataset.createVariable(variablename, 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
    outputvariable[:, :, :] = data
    outputvariable.long_name = long_name
    outputvariable.unit = unit
    dataset.close() 
    print "Created " + os.path.basename(outputNetCDF) + "\nZipping file"
    zippedNetCDF = ZipFile(outputNetCDF)
    print "Created " + os.path.basename(zippedNetCDF) + "\n"
    os.remove(outputNetCDF)
