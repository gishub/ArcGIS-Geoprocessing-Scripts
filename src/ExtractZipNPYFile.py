import numpy, sys, gzip, cPickle, cStringIO, arcpy, os

def getQuadKey(x, y): # returns the quadkey for the passed tile coordinates, e.g. 27025,16973 will return 132320330230021
    quadKey = ""
    y = 32767 - y # the quadkey is based on a y origin based in the northern hemisphere
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey

gzipFileName = arcpy.GetParameterAsText(0)
#gzipFileName = r"E:\cottaan\My Documents\ArcGIS\17975.npygz"
objtype = 1 #species
gzipFileHandle = gzip.open(gzipFileName, 'rb')
(drive, tail) = os.path.split(gzipFileName)
speciesId = tail.split(".")[0].split("/")[-1]
while 1: 
    try:
        gzipUnpickledArray = cPickle.load(gzipFileHandle) # array is a 3d array of the form [x0,x1,xn],[y0,y1,yn],[z0,z1,zn]
        coords = numpy.transpose(gzipUnpickledArray) #convert to an array in coordinate form ([x0,y0,z0],[x1,y1,z1]..)
        fileCopyFrom = cStringIO.StringIO()
        fileCopyFrom.writelines(['\t'.join([speciesId, getQuadKey(coord[0], coord[1]), str(coord[0]), str(coord[1]), str(coord[2]), str(objtype)]) + '\n' for coord in coords])
        fileCopyFrom.seek(0)
        arcpy.AddMessage(fileCopyFrom.getvalue())
        fileCopyFrom.close()
    except EOFError:
        arcpy.AddMessage("reached EOF of ... %s" % speciesId)
        break
    except:
        arcpy.AddMessage("something went wrong... %s" % speciesId)
        break
fileCopyFrom.close()
gzipFileHandle.close()
