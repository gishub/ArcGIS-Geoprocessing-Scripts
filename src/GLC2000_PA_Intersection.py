import arcpy
WDPA_FEATURE_CLASS = "wdpa_latest_11_07_2014"
OUTPUT_TABLE_NAME = "glc2000_pa"
arcpy.AddMessage("Creating a join between " + WDPA_FEATURE_CLASS + " and " + OUTPUT_TABLE_NAME)
arcpy.AddJoin_management(WDPA_FEATURE_CLASS, "id", OUTPUT_TABLE_NAME, "ID")
arcpy.AddMessage("Selecting PAs which have no GLC2000 statistics")
arcpy.SelectLayerByAttribute_management(WDPA_FEATURE_CLASS, "NEW_SELECTION", OUTPUT_TABLE_NAME + ".ID IS NULL")
arcpy.AddMessage("Removing join between " + WDPA_FEATURE_CLASS + " and " + OUTPUT_TABLE_NAME)
arcpy.RemoveJoin_management(WDPA_FEATURE_CLASS, OUTPUT_TABLE_NAME)
arcpy.AddMessage("Exporting the PAs to a temporary feature layer")
arcpy.MakeFeatureLayer_management(WDPA_FEATURE_CLASS, "missing")
arcpy.AddMessage("Getting the GLC2000 statistics for the missing PAs") 
arcpy.gp.TabulateArea_sa("missing", "id", "glc2000_v1_gdal_1", "Value", "in_memory\glc2000_pa_2", "0.0089285714")
result = arcpy.GetCount_management("in_memory\glc2000_pa_2")
arcpy.AddMessage(str(result) + " records created")
arcpy.AddMessage("Appending to the " + OUTPUT_TABLE_NAME + " table")
arcpy.Append_management("in_memory\glc2000_pa_2", OUTPUT_TABLE_NAME, "NO_TEST", "#", "#")
