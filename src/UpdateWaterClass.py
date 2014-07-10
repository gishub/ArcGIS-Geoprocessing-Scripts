import arcpy
fl = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Updating inland points")
arcpy.SelectLayerByLocation_management(fl,"WITHIN","Water class")
arcpy.CalculateField_management(fl,"waterclass","Inland","PYTHON_9.3")
arcpy.AddMessage("Updating coastal points")
arcpy.SelectLayerByLocation_management(fl,"WITHIN","coastal_buffer_500m")
arcpy.AddMessage("Updating marine points")
