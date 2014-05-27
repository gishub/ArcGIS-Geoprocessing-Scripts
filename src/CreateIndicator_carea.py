import win32com.client, os,  netCDF4,subprocess,numpy
from netCDF4 import Dataset
INPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"
OUTPUT_DATA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Data/"

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

engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
queryDef = db.CreateQueryDef("", "SELECT distinct fullpath, archivename,filename FROM DownloadedZipFiles WHERE (((DownloadedZipFiles.filename) Like '*_harea_sea_*'));")
r = queryDef.OpenRecordset()
total=r.RecordCount
counter=1
while not r.EOF:
    gzipfile = str(r.fullpath)
    print "Processing " + os.path.basename(gzipfile) + " (" + str(counter) + "/" + str(total) + ")"
    archivename = str(r.archivename)
    UnzipGZFile(gzipfile, archivename)
    data = Dataset(INPUT_DATA + archivename) 
    outputNetCDF = OUTPUT_DATA + archivename.replace("_harea_sea_", "_carea_sea_")
    outputData = Dataset(outputNetCDF, 'w', format='NETCDF3_CLASSIC') 
    outputData.createDimension(u'lon', data.variables['longitude'].size)
    outputData.createDimension(u'lat', data.variables['latitude'].size) 
    outputData.createDimension(u'time', data.variables['time'].size)
    longitudes = outputData.createVariable(u'lon', 'f4', ('lon',))
    latitudes = outputData.createVariable(u'lat', 'f4', ('lat',))
    times = outputData.createVariable(u'time', 'f8', ('time',))
    outputvariable = outputData.createVariable(u'carea', 'f4', ('time', 'lat', 'lon',), fill_value= -9999)
    longitudes[:] = data.variables['longitude'][:] 
    latitudes[:] = data.variables['latitude'][:]
    times[:] = data.variables['time'][:] 
    outputvariable[0, :, :] = numpy.array(data.variables['CFTfrac'][39, :, :])*5000
    outputData.close() 
    data.close()
    if os.path.exists(INPUT_DATA + archivename):
        os.remove(INPUT_DATA + archivename)
    counter=counter+1
    r.MoveNext()
db.Close()

