import arcpy
input = arcpy.GetParameterAsText(0)
target = arcpy.GetParameterAsText(1)
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(target)
arcpy.Append_management([input], target, "NO_TEST",fieldmappings)