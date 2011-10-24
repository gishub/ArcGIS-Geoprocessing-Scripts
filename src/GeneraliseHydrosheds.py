import arcpy
inputData= arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)
for i in range(1,9):
#    arcpy.Dissolve_management("af_pfaf_gamma_Project","PFAF_" + str(i),"PFAF_" + str(i))
    arcpy.Dissolve_management(inputData,outputWorkspace + "PFAF_" + str(i),"PFAF_" + str(i))