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
                arcpy.AddMessage("Creating output file geodatabase " + valueDimensionStandardName + ".gdb")
                arcpy.CreateFileGDB_management("D:/Users/andrewcottam/Documents/ArcGIS/fao", valueDimensionStandardName + ".gdb")
        arcpy.AddMessage("Loading NetCDF data from " + netCDFFile)
        min_lon = float(data.variables[LONGITUDE_DIMENSION_NAME][0])
        min_lat = float(data.variables[LATITUDE_DIMENSION_NAME][0])
        x_cell_size = float(data.variables[LONGITUDE_DIMENSION_NAME][1]) - min_lon
        y_cell_size = float(data.variables[LATITUDE_DIMENSION_NAME][1]) - min_lat
        decadalindices = self.getDecadalSliceIndices()
        for item in decadalindices:
            arcpy.AddMessage("Producing mean for decade " + item["label"])
            outputname = "D:/Users/andrewcottam/Documents/ArcGIS/fao/" + valueDimensionStandardName + ".gdb/" + valueDimensionStandardName + "_y" + item["label"]
            self.writeSlice(data.variables[valueDimensionName], item["start"], item["end"], min_lon, min_lat, x_cell_size, y_cell_size, outputname)
#         yearlyIndices = self.getSliceIndices(data.variables[TIME_DIMENSION_NAME], "years")
#         for item in yearlyIndices:
#             arcpy.AddMessage("Producing mean for " + str(item["year"]))
#             outputname = "D:/Users/andrewcottam/Documents/ArcGIS/fao/" + valueDimensionStandardName + ".gdb/" + valueDimensionStandardName + "_y" + str(item["year"])
#             self.writeSlice(data.variables[valueDimensionName], item["start"], item["end"], min_lon, min_lat, x_cell_size, y_cell_size, outputname)
        monthlyIndices = self.getSliceIndices(data.variables[TIME_DIMENSION_NAME], "month")
        for item in monthlyIndices:
            arcpy.AddMessage("Producing mean for " + calendar.month_name[item["month"]] + " " + str(item["year"]))
            outputname = "D:/Users/andrewcottam/Documents/ArcGIS/fao/" + valueDimensionStandardName + ".gdb/" + valueDimensionStandardName + "_y" + str(item["year"]) + "_m" + str(item["month"]).zfill(2)
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
    
    def getDecadalSliceIndices(self):
        indices = []
        index1 = date(2010, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        index2 = date(2020, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        index3 = date(2030, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        index4 = date(2040, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        index5 = date(2050, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        index6 = date(2060, 1, 1).toordinal() - date(START_YEAR, 1, 1).toordinal()
        indices.append({"year" : 2020, "start" : index1, "end":index2,"label":"2010-2020"})
        indices.append({"year" : 2030, "start" : index2, "end":index4,"label":"2020-2040"})
        indices.append({"year" : 2040, "start" : index3, "end":index5,"label":"2030-2050"})
        indices.append({"year" : 2050, "start" : index4, "end":index6,"label":"2040-2060"})
        return indices
    
    def writeSlice(self, values, startIndex, endIndex, min_lon, min_lat, x_cell_size, y_cell_size, outputname):
        slice = self.getSlice(values, startIndex, endIndex)
        raster = arcpy.NumPyArrayToRaster(slice, arcpy.Point(min_lon - (x_cell_size / 2), min_lat - (y_cell_size / 2)), x_cell_size, y_cell_size, NO_DATA_VALUE)
        raster.save(outputname)
        sr = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(raster, sr)
        arcpy.ImportMetadata_conversion(r"D:\Users\andrewcottam\Documents\ArcGIS\fao\metadata.xml", "FROM_ISO_19139", raster, "ENABLED")

    def getSlice(self, variable, startIndex, endIndex):
        slice = numpy.mean(variable[startIndex:endIndex, :, :], 0).filled(NO_DATA_VALUE)
        flippedSlice = numpy.flipud(slice)
        return flippedSlice
        
