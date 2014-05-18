import os, arcpy, subprocess
from netCDF4 import Dataset
BASE_PATH = "D:/Users/andrewcottam/Documents/ArcGIS/fao/"
START_TEXT = "Extracting  "
END_TEXT = "Everything"
def unzipGZFile(gzfile, outputfolder, deleteZipfile):
    arcpy.AddMessage("Unzipping " + gzfile + "..")
    p = subprocess.Popen('7z e "' + gzfile + '" -o"' + outputfolder + '" -aos', stdout=subprocess.PIPE)
    result = p.communicate()[0]
    pos = result.find(START_TEXT)
    if pos > -1:
        extractedFilename = result[pos + len(START_TEXT):result.find(END_TEXT) - 4]
        arcpy.AddMessage(extractedFilename + " unzipped")
    else:
        extractedFilename = outputfolder + os.path.basename(gzfile[1:-3])
        arcpy.AddMessage(extractedFilename + " already exists - skipping")
    if deleteZipfile:
        os.remove(gzfile)
        arcpy.AddMessage(gzfile + " deleted")
    return extractedFilename

gzfiles = [u"'D:\\Users\\andrewcottam\\Downloads\\FAO Climate Data Zipped\\ClimAf_1_1960-2100_lpjg_can_wfdei_somd_B1_etotx_sea_tera_ir.nc.gz'"]
for gzfile in gzfiles:
    unzipGZFile(gzfile[1:-1], BASE_PATH + "Input data/", True)
    netCDFFile = BASE_PATH + "Input data/" + os.path.basename(gzfile[1:-4])
    try:
        data = Dataset(netCDFFile)
    except (RuntimeError) as e:
        arcpy.AddError("Unable to load " + netCDFFile + ": " + e.message) 
        pass
        
# os.system('7z e "D:/Users/andrewcottam/Downloads/FAO Climate Data Zipped/somds.wfdei.cmip5.rcp85.GFDL-ESM2M.daily.clt.africa.nc.gz" -o"D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"')
# os.system('7z e "D:/Users/andrewcottam/Downloads/FAO Climate Data Zipped/somds.wfdei.cmip5.rcp85.GFDL-ESM2M.daily.clt.africa.nc.gz" -o"D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Data/"')
