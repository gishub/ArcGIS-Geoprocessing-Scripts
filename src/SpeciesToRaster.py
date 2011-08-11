import arcpy

def getSnapMetres(coord,up):
    if (up==True):
        return (((int(coord/1000))+1)*1000)
    else:
        return (((int(coord/1000))-1)*1000)

#CONSTANT DECLARATIONS
EXTENT_FC = "in_memory\\RangesFC"
PRIORITY_FIELDNAME = "Priority"

#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.rasterStatistics = None
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"
arcpy.env.compression = "PackBits"

#PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

#LOGIC
arcpy.MinimumBoundingGeometry_management(speciesFL, EXTENT_FC, "ENVELOPE", "ALL")
dsc = arcpy.Describe(EXTENT_FC)
extent = dsc.Extent    
arcpy.Delete_management(EXTENT_FC)
minx = getSnapMetres(extent.XMin, False)
maxx = getSnapMetres(extent.XMax, True)
miny = getSnapMetres(extent.YMin, False)
maxy = getSnapMetres(extent.YMax, True)
arcpy.AddMessage("minx:" + str(minx) + " " + "maxx:" + str(maxx) + " " + "miny:" + str(miny) + " " + "maxy:" + str(maxy))
arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)
arcpy.PolygonToRaster_conversion(speciesFL, "ID_NO", outputFile, "MAXIMUM_AREA", PRIORITY_FIELDNAME, 1000)
arcpy.env.extent = None #Reset the extent