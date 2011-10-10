import numpy,arcpy
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
    
file=arcpy.GetParameterAsText(0)
arcpy.AddMessage("Processing " + file)
outputTable=arcpy.GetParameterAsText(1)
prefix=arcpy.GetParameterAsText(2)
speciesID=file.split(prefix)[1][:-4]
data=numpy.load(file) #load the numpy file
data3d=numpy.reshape(data,(3,len(data)/3)) #convert the numpy file to a 3d array ([x0,x1,xn],[y0,y1,yn],[z0,z1,zn])
coords=numpy.transpose(data3d) #convert to coordinates ([x0,y0,z0],[x1,y1,z1]..)
rows = arcpy.InsertCursor(outputTable)
for coord in coords:
    row=rows.newRow()
    row.speciesID=speciesID
    row.quadkey=getQuadKey(coord[0],coord[1]) # get the quad key
    row.mx = coord[0] # populate the x value
    row.my = coord[1] # populate the y value
    row.z = coord[2] # populate the attribute, i.e. the status (native, introduced, extinct etc.)
    rows.insertRow(row)
    del row
del rows
