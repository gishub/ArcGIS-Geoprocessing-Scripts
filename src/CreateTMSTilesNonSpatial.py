import arcpy
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

cur = arcpy.InsertCursor(r"E:\cottaan\My Documents\ArcGIS\Default.gdb\quadkeys")
for x in range(32678):
    for y in range(32678):
        feat = cur.newRow()
        feat.quadkey = getQuadKey(x,y)
        feat.x = x
        feat.y = y
        cur.insertRow(feat)
    arcpy.AddMessage("Col: " + str(x))
del cur        