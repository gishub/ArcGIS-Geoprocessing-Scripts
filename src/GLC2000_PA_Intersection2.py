import arcpy
# intersects the WDPA feature class with the glc2000 dataset by iterating through each PA (as you cant do it as a single dataset because it converts the features to polygons first so overlapping polygons would not appear)
OUTPUT_TABLE = "statistics"
TMP_RASTER = "tmpraster"
TMP_STATS_TABLE = "in_memory\statistics"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"E:\cottaan\My Documents\ArcGIS\PA GLC2000 Analysis\default.gdb"
wdpa_feature_layer = arcpy.GetParameterAsText(0)
glc2000_raster_layer = arcpy.GetParameterAsText(1)
cursor = arcpy.SearchCursor(wdpa_feature_layer)
for row in cursor:
    id = row.getValue("id")
    arcpy.AddMessage("Processing id=" + str(id))
    arcpy.SelectLayerByAttribute_management(wdpa_feature_layer, "NEW_SELECTION", wdpa_feature_layer + ".id=" + str(id))
    arcpy.AddMessage("Converting to raster")
    arcpy.PolygonToRaster_conversion(wdpa_feature_layer, "id", TMP_RASTER, "MAXIMUM_AREA", "id", "0.0089285714")
    arcpy.AddMessage("Getting GLC2000 statistics for " + str(id))
    arcpy.gp.TabulateArea_sa(TMP_RASTER, "Value", glc2000_raster_layer, "Value", TMP_STATS_TABLE, "0.0089285714")
    arcpy.AddMessage("Appending to the statistics table")
    arcpy.Append_management(TMP_STATS_TABLE, OUTPUT_TABLE, "NO_TEST", "#", "#")
    break  
