import arcpy, numpy
#PARAMETERS
speciesRasterLayer = arcpy.GetParameterAsText(0)
outputFile = arcpy.GetParameterAsText(1)

#LOGIC
#convert the raster to a numpy array
myarr=arcpy.RasterToNumPyArray(speciesRasterLayer,"","","",0)
#get all of the indices where the values are 1
indices=numpy.nonzero(myarr==1)
#get the describe object to be able to get the dataset extent
dsc = arcpy.Describe(speciesRasterLayer)
#multiply the row index by 1000
indices[0].__imul__(1000)
#and add the y offset
indices[0].__iadd__(dsc.Extent.YMax)
indices[1].__imul__(1000)
indices[1].__iadd__(dsc.Extent.XMin)
#convert to coordinate pairs
indices2 = numpy.transpose(indices)
#save to file
indices2.tofile(outputFile," ")