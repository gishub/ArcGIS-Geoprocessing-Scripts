import arcpy
FIELDNAME = "rnd"
fl = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Adding field " + FIELDNAME)
arcpy.AddField_management(fl, FIELDNAME, "LONG")
arcpy.AddMessage("Populating field")
arcpy.CalculateField_management(fl, FIELDNAME, "random.randrange(0,100000000)","PYTHON_9.3","import random")