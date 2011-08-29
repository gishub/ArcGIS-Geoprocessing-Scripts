import arcpy, numpy, datetime
#PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)
outputAsKm = arcpy.GetParameterAsText(2) #true is in Km

def getIndices(myarr):
    try:
        return numpy.nonzero(myarr==1)
    except MemoryError:
        arcpy.AddMessage("getIndices - Memory Error")

def getCoords(indices):
    try:
        return numpy.transpose(indices)
    except MemoryError:
        arcpy.AddMessage("getCoords - Memory Error")
    
#LOGIC
#convert the raster to a numpy array
try:
    desc=arcpy.Describe(speciesRasterLayer)
    if (outputAsKm=='true'):
        minx=desc.Extent.XMin/1000
        maxy=desc.Extent.YMax/1000
        ymultiplier=-1
        xmultiplier=1
    else:
        minx=desc.Extent.XMin
        maxy=desc.Extent.YMax
        ymultiplier=-1000
        xmultiplier=1000
    if (desc.width*desc.height<1000000000):
        myarr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0)
        #get all of the indices where the values are 1
        indices=getIndices(myarr)
        del myarr
        if (indices):
            #multiply the row index by -1 or -1000 - it is minus because y values decrease as you move south
            indices[0].__imul__(ymultiplier)
            #and add it from the y offset
            indices[0].__iadd__(maxy)
            indices[1].__imul__(xmultiplier)
            indices[1].__iadd__(minx)
            #convert to coordinate pairs
            indices2 = getCoords(indices)
            del indices
            if not(indices2 is None):
                #save to file
                numpy.save(outputFile,indices2)
                del indices2
    else:
        arcpy.AddMessage("Raster exceeds 1Gb")
except MemoryError:
    arcpy.AddMessage("Something went horribly wrong")