import numpy,arcpy,cPickle
from scipy.sparse import *
from scipy import *
table=arcpy.GetParameterAsText(0)
outputfile=arcpy.GetParameterAsText(1)
count = int(str(arcpy.GetCount_management(table)))
rows = arcpy.SearchCursor(table)
xarr=numpy.zeros([count],int) #initialise an array to hold the data for the x coordinates
yarr=numpy.zeros([count],int) #initialise an array to hold the data for the y coordinates
zarr=numpy.zeros([count],int) #initialise an array to hold the data for the species richness
i = 0
for row in rows: #iterate through the rows
    xarr.put(i,row.tx)
    yarr.put(i,row.ty)
    zarr.put(i,row.COUNT_speciesID)    
    i = i + 1
arcpy.AddMessage("Finished building arrays")
outputArr=numpy.concatenate((xarr,yarr,zarr)) #join the 3 arrays together 
arcpy.AddMessage("Finished joining arrays")
f = open(outputfile,'wb') #write the ndarray out to file
cPickle.dump(outputArr, f, protocol=2)
f.close() 