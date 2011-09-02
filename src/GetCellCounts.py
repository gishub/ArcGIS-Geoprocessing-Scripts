import numpy,arcpy,os
arcpy.env.workspace = r"E:\cottaan\My Documents\SpeciesGridData"
for file in arcpy.ListFiles("*.npy"):
    fileinfo=os.stat(arcpy.env.workspace + os.sep + file)
    if fileinfo.st_size>0:
        cells=numpy.load(arcpy.env.workspace + os.sep + file)
        arcpy.AddMessage(file + "\t" + str(len(cells[0])))