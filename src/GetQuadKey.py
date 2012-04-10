import arcpy, datetime

def getQuadKey(x, y):                                           # returns the quadkey for the passed tile coordinates, e.g. 27025,16973 will return 132320330230021
    quadKey = ""
    y = 32767 - y                                               # the quadkey is based on a y origin based in the northern hemisphere
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey
    
x = arcpy.GetParameter(0)
y = arcpy.GetParameter(1)
arcpy.AddMessage("x: " + str(x) + " y: " + str(y))
quadKey = getQuadKey(x,y)
arcpy.AddMessage("quadKey: " + quadKey)
arcpy.SetParameterAsText(2, quadKey)
