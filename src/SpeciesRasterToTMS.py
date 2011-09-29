import arcpy,numpy,math, cPickle
#INPUT PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)
err="Unable to write to file '" + outputFile + "' "

def getXY(arr): # function that returns only the indices of the cells with data>0
    try:
        xy=numpy.nonzero(arr>0) #get the xy coordinates
        return xy
    except MemoryError:
        arcpy.AddMessage(err + "(Memory error in getting xy coordinates)")

def getValues(arr,xy): # function that returns the values from the raster
    try:
        return arr[xy]
    except MemoryError:
        arcpy.AddMessage(err + "(Memory error in getting raster values)")
    
try:
    desc=arcpy.Describe(speciesRasterLayer) # get the describe object to be able to get the extent of the raster layer
    cellWidth=desc.meanCellWidth
    cellHeight=desc.meanCellHeight
    if (cellWidth==0 or cellHeight==0):
        arcpy.AddMessage(err + "(Raster has no cols/rows)") # workaround for rasterising small polygons in ArcGIS issue - e.g. for species 13132
    else:
        if (math.isinf(cellWidth) or math.isinf(cellHeight)):
            arcpy.AddMessage(err + "(Raster has cells with infinite width/height)") # workaround for rasterising small polygons in ArcGIS issue - e.g. for species 136520
        else:
            if (desc.width*desc.height<1000000000): # hack - for large rasters ArcMap crashes so this like should stop that - probably a memory issue
                arr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0) # convert the raster to a numpy array
                xy=getXY(arr) # get all of the xy coordinates where there are values
                values=getValues(arr,xy) # get the raster values using the xy coordinates
                del arr # delete the full array to free memory
                if (xy): # if there are xy coordinates - i.e. no memory error
                    #get the tile number for the x coordinate
                    xy[1].__iadd__(int(math.floor((desc.Extent.XMin + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
                    #get the tile number for the y coordinate
                    xy[0].__imul__(-1) # y values decrease as you go south
                    xy[0].__iadd__(int(math.floor((desc.Extent.YMax + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
                    #create a new array which is the concatenation of the x indices array, y indices array and the array values
                    outputArr=numpy.concatenate((xy[1],xy[0],values)) # the x and y arrays need to be switched over
                    #output to file
                    f = open(outputFile,'wb')
                    cPickle.dump(outputArr, f, protocol=2)
                    f.close()                
                    del xy # free memory
                    del values
            else:
                arcpy.AddMessage(err + "(Raster exceeds 1Gb)")
except MemoryError:
    arcpy.AddMessage(err + "(Something went horribly wrong)")