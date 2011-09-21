import os.path
exists=os.path.exists(arcpy.GetParameterAsText(0))
if (exists==1):
    arcpy.SetParameterAsText(1,"true") # the first output parameter refers to the true variable
    arcpy.SetParameterAsText(2,"false") # the second output parameter refers to the false variable
    arcpy.AddMessage("File exists")
else:
    arcpy.SetParameterAsText(1,"false") # the first output parameter refers to the true variable
    arcpy.SetParameterAsText(2,"true") # the second output parameter refers to the false variable
    arcpy.AddMessage("File does not exist")