import arcpy
outputFC=arcpy.GetParameterAsText(1)
size=arcpy.GetParameterAsText(0)
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"
mxd=arcpy.mapping.MapDocument("current") #get a pointer to the current map document
dataFrame=arcpy.mapping.ListDataFrames(mxd)[0] #get a pointer to the current data frame
extent=dataFrame.extent #get a pointer to the current extent
xcell=int(math.floor(((extent.upperLeft.X+20037508.3428)/1222.9924525618553))) #calculate the x cell value
ycell=int(math.floor(((extent.upperLeft.Y+20037508.3428)/1222.9924525618553))) #calculate the y cell value
xmin=((xcell*1222.9924525618553)-20037508.3428) #calculate the x value in metres
xminstr1=str(xmin) #calculate the x string to pass into the CreateFishnet tool
xminstr2=str(xmin+1000) #calculate the x2 string to pass into the CreateFishnet tool
yminstr=str((ycell*1222.9924525618553)-20037508.3428) #calculate the y value in metres
#create the fishnet - this runs only once and subsequent attempts crash ArcMap for some reason - unable to find out the cause
arcpy.CreateFishnet_management(outputFC, xminstr1 + " " + yminstr, xminstr2 + " " + yminstr, "1222.9924525618553", "1222.9924525618553", size, size, "#", "NO_LABELS")
del mxd