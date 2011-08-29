import arcpy
path = arcpy.GetParameterAsText(0)
arcpy.env.workspace = path
rasterList = arcpy.ListRasters("*")
arcpy.AddMessage("raster\trows\tcols")
for raster in rasterList:    
    desc = arcpy.Describe(raster)
    arcpy.AddMessage(raster + "\t" + str(desc.height) + "\t" + str(desc.width))