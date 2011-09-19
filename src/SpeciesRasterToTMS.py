import arcpy,numpy,math, cPickle
#INPUT PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)
err="Unable to write to file '" + outputFile + "' "

def getData(arr2): # function that returns only the indices of the cells with data==1
    try:
        xy=numpy.nonzero(arr2>0) #get the xy coordinates
        values=arr2[xy] #get the raster values
        return xy,values
    except MemoryError:
        arcpy.AddMessage(err + "(Memory error)")
    
try:
    desc=arcpy.Describe(speciesRasterLayer) # get the describe object to be able to get the extent of the raster layer
    if (desc.meanCellWidth==0):
        arcpy.AddMessage(err + "(Raster has no cols/rows)") # hack - if the polygon is smaller than the raster cell size it will not be rasterized
    else:
        if (desc.width*desc.height<1000000000): # hack - for large rasters ArcMap crashes so this like should stop that - probably a memory issue
            arr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0) # convert the raster to a numpy array
            xy,values=getData(arr) # get all of the xy coordinates and the values where the values are not NoData
            del arr # delete the full array to free memory
            if (xy): # if there are xy coordinates - i.e. no memory error
                #get the tile number for the x coordinate
                xy[1].__iadd__(int(math.floor((desc.Extent.XMin + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
                #get the tile number for the y coordinate
                xy[0].__imul__(-1) # y values decrease as you go south
                xy[0].__iadd__(int(math.floor((desc.Extent.YMax + 20037508.3428) / 1222.9924525618553))) # 20037508.3428m is the origin shift and 1222.9924525618553m is the cell size
                #create a new array which is the concatenation of the x indices array, y indices array and the array values
                outputArr=numpy.concatenate((xy[0],xy[1],values))
                arcpy.AddMessage("3")       
                #output to file
                f = open(outputFile,'wb')
                cPickle.dump(outputArr, f, protocol=2)
                f.close()                
                del data # free memory
        else:
            arcpy.AddMessage(err + "(Raster exceeds 1Gb)")
except MemoryError:
    arcpy.AddMessage(err + "(Something went horribly wrong)")