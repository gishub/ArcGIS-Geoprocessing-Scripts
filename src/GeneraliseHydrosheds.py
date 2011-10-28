import arcpy
for i in range(1,10):
    name="PFAF_" +str(i)
    arcpy.Dissolve_management(r"D:\GIS Data\Andrew\FreshwaterData.gdb\af_pfaf_gamma_Project",name,name)
    arcpy.AddIndex_management(name,name,name + "i")