import arcpy,numpy,math
#PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

def getData(arr):
    try:
        return numpy.nonzero(arr==1)
    except MemoryError:
        arcpy.AddMessage("getIndices - Memory Error")

def getQuadKey(x,y): # x,y tile coordinates, e.g. 27025,16973
    quadKey = ""
    y = 32767 -y
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i-1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey
    
#LOGIC
#convert the raster to a numpy array
try:
    desc=arcpy.Describe(speciesRasterLayer)
    if (desc.width*desc.height<1000000000):
        arr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0)
        #get all of the data where the values are not NoData
        data=getData(arr)
        del arr
        if (data):
            #get the tile number for the x coordinate
            data[1].__iadd__(int(math.floor((desc.Extent.XMin + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
            #get the tile number for the y coordinate
            data[0].__imul__(-1) # y values decrease as you go south
            data[0].__iadd__(int(math.floor((desc.Extent.YMax + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
#            for i in range(len(data[0])):
#                quadTree = getQuadKey(data[1][i],data[0][i])
#                arcpy.AddMessage(quadTree)
            numpy.save(outputFile,data)
            del data
    else:
        arcpy.AddMessage("Raster exceeds 1Gb")
except MemoryError:
    arcpy.AddMessage("Something went horribly wrong")