import arcpy
    
#CONSTANT DECLARATIONS
PRIORITY_FIELDNAME = "Priority"

#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"

#PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

#LOGIC
arcpy.env.snapRaster = r"E:\cottaan\My Documents\ArcGIS\Default.gdb\SnapGrid"
arcpy.PolygonToRaster_conversion(speciesFL,"ID_NO", outputFile, "MAXIMUM_AREA", PRIORITY_FIELDNAME,"1222.99245256186") # grid size for zoom level 15 in Web Mercator