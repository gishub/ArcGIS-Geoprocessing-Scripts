import arcpy, math

def quadkeyToXY(quadkey):
    tileX = tileY = 0
    level = len(quadkey)
    for i in range(level, 0, -1):
        mask = 1 << (i - 1)
        if (quadkey[level - i] == "1"):
            tileX |= mask
        if (quadkey[level - i] == "2"):
            tileY |= mask
        if (quadkey[level - i] == "3"):
            tileX |= mask
            tileY |= mask
    tileY = (pow(2, level)) - tileY - 1
    return tileX, tileY
    
quadkey = arcpy.GetParameter(0)
arcpy.AddMessage("quadkey: " + quadkey)
x, y = quadkeyToXY(quadkey)
arcpy.AddMessage("x: " + str(x) + " y: " + str(y))
arcpy.SetParameter(1, x)
arcpy.SetParameter(2, y)