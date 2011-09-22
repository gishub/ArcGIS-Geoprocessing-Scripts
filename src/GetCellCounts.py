import numpy,arcpy,os
path = arcpy.GetParameterAsText(0)
arcpy.env.workspace = path
for file in arcpy.ListFiles("*.npy"):
    fileinfo=os.stat(arcpy.env.workspace + os.sep + file)
    if fileinfo.st_size>0:
        cells=numpy.load(arcpy.env.workspace + os.sep + file)
        arcpy.AddMessage(file + "\t" + str(len(cells)/3)) #the data are saved as x array, y array and values array
        del cells