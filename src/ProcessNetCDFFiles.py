import sys, os, datetime, bisect, numpy, arcpy, zipfile, glob, logging
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset
LATITUDE_DIMENSION_NAME = "lat"
LONGITUDE_DIMENSION_NAME = "lon"
TIME_DIMENSION_NAME = "time"
NO_DATA_VALUE = -1
OUTPUT_DATA_LTA = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Data LTA/"
OUTPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Output Zips/"

def zipFolder(zipfilename, deleteFiles=False):
    zip = zipfile.ZipFile(OUTPUT_ZIPS + zipfilename + ".zip", "w", zipfile.ZIP_DEFLATED, True)
    files = glob.glob(OUTPUT_DATA_LTA + zipfilename + "*")
    for file in files:
        zip.write(file , os.path.basename(file))
        if deleteFiles:
            os.remove(file)
    zip.close()

def writeSlices(values, slices, min_lon, min_lat, x_cell_size, y_cell_size, filename):
    for slice in slices:  
        if values.ndim < 3:
            logging.error("\t\tValue dimensions are <3")
            print "\t\tValue dimensions are <3"
            return      
        if slice['start'] == slice['end']:
            dataSlice = values[slice['start'], :, :].filled(NO_DATA_VALUE)
        else:
            dataSlice = numpy.mean(values[slice['start']:slice['end'], :, :], 0).filled(NO_DATA_VALUE)
        raster = arcpy.NumPyArrayToRaster(dataSlice, arcpy.Point(min_lon - (x_cell_size / 2), min_lat - (y_cell_size / 2)), x_cell_size, y_cell_size, NO_DATA_VALUE)
        outputfile = filename[:-3] + slice["label"] + ".tif"
        logging.info("\t\tWriting '" + outputfile + "'")
        print "\t\tWriting '" + outputfile + "'" 
        raster.save(OUTPUT_DATA_LTA + outputfile)
        sr = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(raster, sr)

def GetNetCDFOrdinals(data, startDate):
    '''Returns an array of proleptic gregrian dates for the passed netcdf'''
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
    if dateInterval == "day":
        totaldays = ((d2 - d1).days) + 1
        dates = [dateFrom + relativedelta(days=i) for i in range(totaldays)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_d" + d.strftime("%j")} for d in dates]
    elif dateInterval == "month":
        totalmonths = (diff.years * 12 + diff.months) + 1
        dates = [dateFrom + relativedelta(months=i) for i in range(totalmonths)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year) + "_m" + str(d.month).zfill(2)} for d in dates]
    elif dateInterval == "year":
        totalyears = diff.years + 1
        dates = [dateFrom + relativedelta(years=i) for i in range(totalyears)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_y" + str(d.year)} for d in dates]
    elif dateInterval[:3] == "lta":
        interval = int(dateInterval[3:])
        totalCount = (diff.years / interval) + 1
        dates = [dateFrom + relativedelta(years=(i * interval)) for i in range(totalCount)]
        dateBins = [{"ordinal":d.toordinal(), "label":"_yy" + str(d.year) + "_" + str(d.year + interval)} for d in dates]
    return dateBins

def OutputSlices(data, variableNames, d1, d2, dateInterval, filename):
    for variableName in variableNames['valueNames']:
        if 'long_name' in dir(data.variables[variableName]):
            logging.info("\t\tProcessing: " + data.variables[variableName].long_name + " (" + variableName + ")")
            print "\t\tProcessing: " + data.variables[variableName].long_name + " (" + variableName + ")"
        else:
            logging.info("\t\tProcessing: " + variableName)
            print "\t\tProcessing: " + variableName
        min_lon = min(data.variables[variableNames['lonName']])
        min_lat = min(data.variables[variableNames['latName']])
        x_cell_size = float(data.variables[variableNames['lonName']][1]) - min_lon
        y_cell_size = x_cell_size
    #     gets the bins that the netcdf file data will be split into - each bin will have proleptic gregorian date number
        dateBins = GetDateBins(d1, d2, dateInterval)
#         print "dateBins:"
#         print dateBins
    #     get the proleptic dates for the netcdf data
#         print "data:"
#         print data
        ordinals = GetNetCDFOrdinals(data, d1)
#         print "ordinals:"
#         print ordinals
    #     get the indices for the netcdf data for each bin
        indices = [bisect.bisect_left(ordinals, bin['ordinal']) for bin in dateBins]
#         print "indices:"
#         print indices
    #     create the slices information for writing out the slices
        slices = [{"start":indices[i - 1], "end":indices[i] - 1, "label":dateBins[i - 1]['label']} for i in range(1, len(indices))]
#         print "slices:"
#         print slices
        writeSlices(data.variables[variableName], slices, min_lon, min_lat, x_cell_size, y_cell_size, filename)

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
    
def ProcessFile(file, frequency):
    logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    arcpy.env.overwriteOutput = True
    filename = os.path.basename(file)
    logging.info("Processing:\t'" + filename + "' for " + frequency + " intervals")
    print "Processing:\t'" + filename + "' for " + frequency + " intervals"
    data = Dataset(file)
    variableNames = GetVariables(data)
    logging.info("\t\t" + str(variableNames))
    print "\t\t" + str(variableNames)
    slices = int(data.variables[variableNames['timeName']].size)
    logging.info("\t\tTime slices: " + str(slices))
    print "\t\tTime slices: " + str(slices)
    logging.info("\t\tTime units (from NetCDF metadata): " + data.variables[variableNames['timeName']].units)
    print "\t\tTime units (from NetCDF metadata): " + data.variables[variableNames['timeName']].units
    logging.info("Slicing:\t")
    print "Slicing:\t"
    d1 = datetime.datetime(1960, 1, 1)
    d2 = datetime.datetime(2100 , 1, 1)
    OutputSlices(data, variableNames, d1, d2, frequency, filename)
    data.close()
    zipFolder(filename[:-4])

if __name__ == "__main__":
    args = sys.argv
    ProcessFile(args[1], args[2])
