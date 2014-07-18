# Iterates through all feature classes in a feature dataset and computes the zonal statistics for each feature class and appends the results into a single output table
import arcpy
arcpy.CheckOutExtension("Spatial")
feature_dataset = arcpy.GetParameterAsText(0)  # get the featuredataset
zone_field = arcpy.GetParameterAsText(1)  # get the zone_field
input_raster = arcpy.GetParameterAsText(2)  # get the input raster
class_field = arcpy.GetParameterAsText(3)  # get the class_field
output_table_name = arcpy.GetParameterAsText(4)  # get the output table name
desc = desc = arcpy.Describe(feature_dataset)
filegdbpath = desc.path
arcpy.env.workspace = feature_dataset
featureclasses = arcpy.ListFeatureClasses()
for featureclass in featureclasses:  # iterate through the feature classes
    arcpy.AddMessage("TabulateArea for " + featureclass)
    
    arcpy.gp.TabulateArea_sa(featureclass, "wdpaid", "E:/cottaan/My Documents/ArcGIS/PA GLC2000 Analysis/default.gdb/glc2000_v1_gdal_1", "Value", "E:/cottaan/My Documents/ArcGIS/Default.gdb/Tabulat_wdpa_la1", "0.0089285714")
    
