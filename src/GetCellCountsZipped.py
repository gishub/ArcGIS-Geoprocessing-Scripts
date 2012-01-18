import numpy, arcpy, os, cPickle, gzip
path = arcpy.GetParameterAsText(0)
arcpy.env.workspace = path
for file in arcpy.ListFiles("*.npygz"):
    gzipFileName = arcpy.env.workspace + os.sep + file
    fileinfo = os.stat(gzipFileName)
    if fileinfo.st_size > 0:
        gzipFileHandle = gzip.open(gzipFileName, 'rb')
        gzipArray = cPickle.load(gzipFileHandle)
        arcpy.AddMessage(file + "\t" + str(len(gzipArray[0]))) #the data are saved as x array, y array and values array