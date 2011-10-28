import arcpy
import math

def getQuadKey(x,y): # returns the quadkey for the passed tile coordinates, e.g. 27025,16973 will return 132320330230021
    quadKey = ""
    y=32767-y
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i-1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey

def MetersToLatLon(x,y):
    lon = (x / SHIFT) * 180.0
    lat = (y / SHIFT) * 180.0
    lat = 180 / math.pi * (2 * math.atan( math.exp( lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon

SHIFT = 2 * math.pi * 6378137 / 2.0 #20037508.3
CELLSIZE = 2 * math.pi * 6378137 / 32768 #1222.99245
size=int(arcpy.GetParameterAsText(0))
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"
mxd=arcpy.mapping.MapDocument("current") #get a pointer to the current map document
dataFrame=arcpy.mapping.ListDataFrames(mxd)[0] #get a pointer to the current data frame
extent=dataFrame.extent #get a pointer to the current extent
xcell=int(math.floor(((extent.upperLeft.X+SHIFT)/CELLSIZE))) #calculate the x cell value
ycell=int(math.floor(((extent.upperLeft.Y+SHIFT)/CELLSIZE))) #calculate the y cell value
xmin=((xcell*CELLSIZE)-SHIFT) #calculate the x value in metres
ymin=((ycell*CELLSIZE)-SHIFT) #calculate the y value in metres
cur = arcpy.InsertCursor(r"E:\cottaan\My Documents\ArcGIS\Default.gdb\WebMercator\TMS_Tiles")
pntObj = arcpy.Point()
arrayObj = arcpy.Array()
for x in range(xcell,xcell+size):
    for y in range(ycell-size,ycell):
        for vertex in [0,1,2,3,4]:
            if vertex in [0,3,4]:
                pntObj.X = (CELLSIZE*(x+1)) - SHIFT
            else:
                pntObj.X = (CELLSIZE*x) - SHIFT
            if vertex in [0,1,4]:
                pntObj.Y = (CELLSIZE*(y+1)) - SHIFT
            else:
                pntObj.Y = (CELLSIZE*y) - SHIFT
            arrayObj.add(pntObj)
        feat = cur.newRow()
        feat.quadkey = getQuadKey(x,y)
        feat.x = x
        feat.y = y
        lat, long = MetersToLatLon(arrayObj[1].X,arrayObj[1].Y)
        feat.lat = lat
        feat.long = long   
        feat.shape = arrayObj
        cur.insertRow(feat)
        arrayObj.removeAll()
del cur        
del mxd