import arcpy
    
#CONSTANT DECLARATIONS
PRIORITY_FIELDNAME = "wdpaid" # this is a bit of a hack but basically we can use this as the priority field to ensure that if the feature in question overlaps the cell by less than 50% then it will be selected

#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"

#PARAMETERS
paFL = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

#LOGIC
arcpy.env.snapRaster = r"E:\cottaan\My Documents\ArcGIS\Default.gdb\SnapGrid"
arcpy.PolygonToRaster_conversion(paFL,"wdpaid", outputFile, "MAXIMUM_AREA", PRIORITY_FIELDNAME,"1222.9924525618553") # 1222.9924525618553 is the grid size for zoom level 15 in Web Mercator