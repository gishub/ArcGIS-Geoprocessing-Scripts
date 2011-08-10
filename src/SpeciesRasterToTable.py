import arcpy
import numpy 
speciesRaster = arcpy.GetParameterAsText(0)
outputTable = arcpy.GetParameterAsText(1)
#speciesRaster = r"E:\cottaan\My Documents\ArcGIS\Default.gdb\ID17975"
#outputTable = r"E:\cottaan\My Documents\ArcGIS\SpeciesRangeTable.dbf"
desc = arcpy.Describe(speciesRaster)
xmin = desc.Extent.XMin
ymax = desc.Extent.YMax
myArray = arcpy.RasterToNumPyArray(speciesRaster)
rows = arcpy.InsertCursor(outputTable)
iter = myArray.flat
offset = myArray.strides[0]
counter = 0
for item in iter:
    if (item!=255):
        row = counter/offset
        col = counter % offset
        x = int(xmin + (col*1000) + 500)
        y = int(ymax - (row*1000) - 500)
        row = rows.newRow() 
        row.x = x
        row.y = y
        row.val = int(item)
        rows.insertRow(row) 
    counter += 1
    