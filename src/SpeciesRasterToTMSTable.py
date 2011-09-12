import arcpy,numpy,math
#INPUT PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputTable = arcpy.GetParameterAsText(1)
speciesID = arcpy.GetParameterAsText(2)

def getData(arr2): # function that returns only the indices of the cells with data==1
    try:
        return numpy.nonzero(arr2==1)
    except MemoryError:
        arcpy.AddMessage("getData - Memory Error")

def getQuadKey(x,y): # returns the quadkey for the passed tile coordinates, e.g. 27025,16973 will return 132320330230021
    quadKey = ""
    y = 32767 -y # the quadkey is based on a y origin based in the northern hemisphere
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i-1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey
    
try:
    desc=arcpy.Describe(speciesRasterLayer) # get the describe object to be able to get the extent of the raster layer
    arcpy.env.overwriteOutput=True
    rows = arcpy.InsertCursor(outputTable)
    if (desc.width*desc.height<1000000000): # hack - for large rasters ArcMap crashes so this like should stop that - probably a memory issue
        arr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0) # convert the raster to a numpy array       
        data=getData(arr) # get all of the data where the values are not NoData
        del arr # delete the full array to free memory
        if (data): # if there is data
            #get the tile number for the x coordinate
            data[1].__iadd__(int(math.floor((desc.Extent.XMin + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
            #get the tile number for the y coordinate
            data[0].__imul__(-1) # y values decrease as you go south
            data[0].__iadd__(int(math.floor((desc.Extent.YMax + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
            for i in range(len(data[0])):
                row=rows.newRow()
                row.speciesID=speciesID
                row.x=data[0][i]
                row.y=data[1][i]
                rows.insertRow(row)
            del data # free memory
            del row
            del rows
    else:
        arcpy.AddMessage("Raster exceeds 1Gb")
except MemoryError:
    arcpy.AddMessage("Something went horribly wrong")
 