import arcpy,numpy,math
#INPUT PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

def getData(arr2): # function that returns only the indices of the cells with data==1
    try:
        return numpy.nonzero(arr2==1)
    except MemoryError:
        arcpy.AddMessage("Memory error: Unable to write to file " + outputFile)
    
try:
    desc=arcpy.Describe(speciesRasterLayer) # get the describe object to be able to get the extent of the raster layer
    if (desc.meanCellWidth==0):
        arcpy.AddMessage("Raster has no cols/rows: Unable to write to file " + outputFile) # hack - if the polygon is smaller than the raster cell size it will not be rasterized
    else:
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
                numpy.save(outputFile,data) # save the tile coordinates to a binary file
                del data # free memory
        else:
            arcpy.AddMessage("Raster exceeds 1Gb: Unable to write to file " + outputFile)
except MemoryError:
    arcpy.AddMessage("Something went horribly wrong: Unable to write to file " + outputFile)