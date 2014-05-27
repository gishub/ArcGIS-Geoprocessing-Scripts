import sys, os, datetime, bisect, numpy, arcpy, zipfile, glob, logging
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset
LATITUDE_DIMENSION_NAME = "lat"
LONGITUDE_DIMENSION_NAME = "lon"
TIME_DIMENSION_NAME = "time"
NO_DATA_VALUE = -1
OUTPUT_DATA_LTA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Data LTA/"
OUTPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Zips/"

def zipFolder(zipfilename):
    zip = zipfile.ZipFile(OUTPUT_ZIPS + zipfilename + ".zip", "w", zipfile.ZIP_DEFLATED, True)
    files = glob.glob(OUTPUT_DATA_LTA + zipfilename + "*")
    for file in files:
        zip.write(file , os.path.basename(file))
        os.remove(file)
    zip.close()

def writeSlices(values, slices, min_lon, min_lat, x_cell_size, y_cell_size, filename, groupby):
    outputFiles = []
    for slice in slices:  
        print "Creating " + slice["label"] + " from " + str(slice['start']) + " to " + str(slice['end'])
        if values.ndim < 3:
            logging.error("\t\tValue dimensions are <3")
            return      
        if slice['start'] == slice['end']:
            dataSlice = values[slice['start'], :, :].filled(NO_DATA_VALUE)
        else:
            if groupby == "mean":
                dataSlice = numpy.mean(values[slice['start']:slice['end'], :, :], 0).filled(NO_DATA_VALUE)
            elif groupby == "sum":
                dataSlice = numpy.sum(values[slice['start']:slice['end'], :, :], 0).filled(NO_DATA_VALUE)
        raster = arcpy.NumPyArrayToRaster(dataSlice, arcpy.Point(min_lon - (x_cell_size / 2), min_lat - (y_cell_size / 2)), x_cell_size, y_cell_size, NO_DATA_VALUE)
        outputfile = filename[:-3] + slice["label"] + ".tif"
        logging.info("\t\tWriting '" + outputfile + "'")
        raster.save(OUTPUT_DATA_LTA + outputfile)
        outputFiles.append(OUTPUT_DATA_LTA + outputfile)
        sr = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(raster, sr)
    print outputFiles

def GetNetCDFOrdinals(data, startDate):
    '''Returns an array of proleptic gregorian dates for the passed netcdf'''
    t = data.variables['time']
    if t.size == 0:
        return ""
    elif  t.size <= 141:  # probably years 141 is from 1960-2100
        return [(startDate + relativedelta(years=i)).toordinal() for i in range(len(t))]
    elif t.size == 564:
        return [(startDate + relativedelta(years=i)).toordinal() for i in range(len(t))]
    elif t.size == 1692:
        return [(startDate + relativedelta(months=i)).toordinal() for i in range(len(t))]
    elif t.size > 1692:
        return [(startDate + relativedelta(days=i)).toordinal() for i in range(len(t))]

def GetDateBins(dateFrom, dateTo, dateInterval):
    '''Gets DateBins from the start date to the end date - including the end date'''
    diff = relativedelta(dateTo, dateFrom)
    if dateInterval == "day":  # bins for daily data
        totaldays = ((binEndDate - binStartDate).days) + 1
        dates = [dateFrom + relativedelta(days=i) for i in range(totaldays)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_d" + d.strftime("%j")} for d in dates]
    elif dateInterval == "month":  # bins for monthly data
        totalmonths = (diff.years * 12 + diff.months) + 1
        dates = [dateFrom + relativedelta(months=i) for i in range(totalmonths)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_m" + str(d.month).zfill(2)} for d in dates]
    elif dateInterval == "year":  # bins for yearly data
        totalyears = diff.years + 1
        dates = [dateFrom + relativedelta(years=i) for i in range(totalyears)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year)} for d in dates]
    elif dateInterval[:3] == "lta":  # bins for long-terma average data
        interval = int(dateInterval[3:])
        totalCount = (diff.years / interval) + 1
        dates = [dateFrom + relativedelta(years=(i * interval)) for i in range(totalCount)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_yy" + str(d.year) + "_" + str(d.year + interval)} for d in dates]
    return dateBins

def OutputSlices(data, variableNames, binStartDate, binEndDate, dateInterval, filename, groupby, datastartdate):
    for variableName in variableNames['valueNames']:
        if 'long_name' in dir(data.variables[variableName]):
            logging.info("\t\tProcessing: " + data.variables[variableName].long_name + " (" + variableName + ")")
        else:
            logging.info("\t\tProcessing: " + variableName)
        min_lon = min(data.variables[variableNames['lonName']])
        min_lat = min(data.variables[variableNames['latName']])
        x_cell_size = float(data.variables[variableNames['lonName']][1]) - min_lon
        y_cell_size = x_cell_size
    #     gets the bins that the netcdf file data will be split into - each bin will have proleptic gregorian date number
        dateBins = GetDateBins(binStartDate, binEndDate, dateInterval)
        ordinals = GetNetCDFOrdinals(data, datastartdate)
        indices = [bisect.bisect_left(ordinals, bin['ordinal']) for bin in dateBins]
        slices = [{"start":indices[i - 1], "end":indices[i] - 1, "label":dateBins[i - 1]['label']} for i in range(1, len(indices))]
        writeSlices(data.variables[variableName], slices, min_lon, min_lat, x_cell_size, y_cell_size, filename, groupby)

def GetVariables(data):
    valueNames = []
    keys = data.variables.keys()
    if LATITUDE_DIMENSION_NAME in keys:
        latName = LATITUDE_DIMENSION_NAME
    else:
        latName = 'latitude'
    if LONGITUDE_DIMENSION_NAME in keys:
        lonName = LONGITUDE_DIMENSION_NAME
    else:
        lonName = 'longitude'
    for key in data.variables:
        if key not in [latName, lonName, TIME_DIMENSION_NAME]:     
            valueNames.append(key)
    return {'latName':latName, 'lonName':lonName, 'valueNames':valueNames, 'timeName':TIME_DIMENSION_NAME}
    
def ProcessFile(file, frequency, groupby, ZipOuput):
    '''processes a netcdf file with the required frequncy. groupby can be 'mean', 'sum' etc.'''
    logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    arcpy.env.overwriteOutput = True
    # get the filename of the netcdf file
    filename = os.path.basename(file)
    logging.info("Processing:\t'" + filename + "' for " + frequency + " intervals")
    # load the netcdf file into memory
    data = Dataset(file)
    # get the names of all of the variables
    variableNames = GetVariables(data)
    logging.info("\t\t" + str(variableNames))
    # get the number of slices of time in the data
    slices = int(data.variables[variableNames['timeName']].size)
    logging.info("\t\tTime slices: " + str(slices))
    logging.info("\t\tTime units (from NetCDF metadata): " + data.variables[variableNames['timeName']].units)
    logging.info("Slicing:\t")
    # slice the data into the required slices
    # set the range of the bin data
    if filename[0:5] == "ClimAf":
        binStartDate = datetime.datetime(int(filename[9:13]), 1, 1)
        binEndDate = datetime.datetime(int(filename[14:18]) , 1, 1)
    else:
        binStartDate = datetime.datetime(1960, 1, 1)
        binEndDate = datetime.datetime(2100, 1, 1)
    datastartdate = datetime.datetime(1960, 1, 1)
    # output the slices - the filename is of the form 'ClimAf_1_1960-2100_lpjg_can_wfdei_somd_B1_etotx_sea_tera_ir.nc' and is a stub for the output zip
    OutputSlices(data, variableNames, binStartDate, binEndDate, frequency, filename, groupby, datastartdate)
    # close the netcdf file
    data.close()
    # zip all files that match the filename pattern in a single zip
    if ZipOuput == "true":
        zipFolder(filename[:-4])

if __name__ == "__main__":
    args = sys.argv
    ProcessFile(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\Input Data\somds.wfdei.cmip5.rcp85.CanESM2.daily.pr.africa.nc", "year", "mean", False)
#     ProcessFile(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\Input Data\ClimAf_1_1960-2100_lpjg_can_wfdei_somd_B1_etotx_sea_teco_ir.nc", "lta5", "mean", False)
#     ProcessFile(args[1], args[2], args[3], args[4])  # fourth argument controls what is done with the results - True will zip them and delete intermediates, False will leave intermediates and not zip them
