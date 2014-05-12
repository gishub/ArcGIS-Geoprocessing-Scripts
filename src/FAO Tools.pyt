import netCDF4, arcpy, numpy, calendar
from netCDF4 import Dataset
from datetime import date
LATITUDE_DIMENSION_NAME = "lat"
LONGITUDE_DIMENSION_NAME = "lon"
TIME_DIMENSION_NAME = "time"
NO_DATA_VALUE = -1
START_YEAR = 1960

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FAO Toolbox"
        self.alias = "FAO Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [SummariseClimateData]

class SummariseClimateData(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SummariseClimateData"
        self.description = "Summarises a set of climatic data from a NetCDF file"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input NetCDF file",
            name="in_filename",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["nc"]
        param0.value = r"D:\Users\andrewcottam\Documents\ArcGIS\fao\FAO Climate Data\somds.wfdei.cmip5.rcp85.CanESM2.daily.clt.africa.nc"
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        netCDFFile = parameters[0].valueAsText
        data = Dataset(netCDFFile)
        for key in data.variables:
            if key not in [LATITUDE_DIMENSION_NAME, LONGITUDE_DIMENSION_NAME, TIME_DIMENSION_NAME]:     
                valueDimensionName = key
                valueDimensionStandardName = data.variables[valueDimensionName].standard_name.encode("ascii", "ignore")
        arcpy.AddMessage("Loading NetCDF data for dimension " + valueDimensionStandardName)
        min_lon = float(data.variables[LONGITUDE_DIMENSION_NAME][0])
        min_lat = float(data.variables[LATITUDE_DIMENSION_NAME][0])
        x_cell_size = float(data.variables[LONGITUDE_DIMENSION_NAME][1]) - min_lon
        y_cell_size = float(data.variables[LATITUDE_DIMENSION_NAME][1]) - min_lat
        yearlyIndices = self.getSliceIndices(data.variables[TIME_DIMENSION_NAME], "years")
        for item in yearlyIndices:
            arcpy.AddMessage("Producing mean for " + str(item["year"]))
            outputname = valueDimensionStandardName + "_y" + str(item["year"])
            self.writeSlice(data.variables[valueDimensionName], item["start"], item["end"], min_lon, min_lat, x_cell_size, y_cell_size, outputname)
        monthlyIndices = self.getSliceIndices(data.variables[TIME_DIMENSION_NAME], "month")
        for item in monthlyIndices:
            arcpy.AddMessage("Producing mean for " + calendar.month_name[item["month"]] + " " + str(item["year"]))
            outputname = valueDimensionStandardName + "_y" + str(item["year"]) + "_m" + str(item["month"]).zfill(2)
            self.writeSlice(data.variables[valueDimensionName], item["start"], item["end"], min_lon, min_lat, x_cell_size, y_cell_size, outputname)
        return

    def getSliceIndices(self, timeArray, groupBy):
        indices = []
        last_day = date.fromordinal(date(START_YEAR, 1, 1).toordinal() + timeArray.size)
        for j in range(START_YEAR, last_day.year + 2):
            if groupBy == "month":
                for i in range(1, 13):
                    index = date(j, i, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
                    indices.append({"year" : j, "month" : i, "start" : index})
            else:
                index = date(j, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
                indices.append({"year" : j, "start" : index})
        for i in range(len(indices)):
            if indices[i + 1]["start"] > timeArray.size:
                indices[i]["end"] = timeArray.size
                break
            else:
                indices[i]["end"] = indices[i + 1]["start"]
                continue
            break
        return indices[:i + 1]
    
    def writeSlice(self, values, startIndex, endIndex, min_lon, min_lat, x_cell_size, y_cell_size, outputname):
        slice = self.getSlice(values, startIndex, endIndex)
        raster = arcpy.NumPyArrayToRaster(slice, arcpy.Point(min_lon - (x_cell_size / 2), min_lat - (y_cell_size / 2)), x_cell_size, y_cell_size, NO_DATA_VALUE)
        arcpy.DefineProjection_management(raster, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
        raster.save("D:/Users/andrewcottam/Documents/ArcGIS/fao/New File Geodatabase.gdb/" + outputname)

    def getSlice(self, variable, startIndex, endIndex):
        slice = numpy.mean(variable[startIndex:endIndex, :, :], 0).filled(NO_DATA_VALUE)
        flippedSlice = numpy.flipud(slice)
        return flippedSlice
        
