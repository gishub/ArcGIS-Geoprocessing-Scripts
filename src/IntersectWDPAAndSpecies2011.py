import arcpy
workspace=arcpy.GetParameterAsText(0)
tablename=arcpy.GetParameterAsText(1)
speciesLayer=arcpy.GetParameterAsText(2)
wdpaLayer=arcpy.GetParameterAsText(3)
outputTable = arcpy.CreateTable_management(workspace, tablename)
arcpy.AddMessage("Creating intersections table")
arcpy.AddField_management(outputTable, "ID_NO", "TEXT")
arcpy.AddField_management(outputTable, "wdpaid", "LONG")
insertCursor = arcpy.InsertCursor(outputTable)
rows = arcpy.SearchCursor(speciesLayer)
rowCount = arcpy.GetCount_management(speciesLayer)
i = 0
start = True
for row in rows:
    i = i + 1
#    if (row.ID_NO == '4310'): # can be used to start the code at a particular ID_NO again if it crashes 
#        start = True
    if (start == True):
        arcpy.AddMessage("Processing: " + row.ID_NO + "\t" + row.BINOMIAL + " (" + str(i) + " out of " + str(rowCount) + ") (" + str(datetime.datetime.now()) + ")")
        arcpy.SelectLayerByAttribute_management(speciesLayer, "NEW_SELECTION", "ID_NO='" + row.ID_NO + "'")
        arcpy.SelectLayerByLocation_management(wdpaLayer, "INTERSECT", speciesLayer)
        paCursor = arcpy.SearchCursor(wdpaLayer)
        for pa in paCursor:
            newRow = insertCursor.newRow()
            newRow.ID_NO = row.ID_NO
            newRow.wdpaid = pa.wdpaid
            insertCursor.insertRow(newRow)
        del newRow
    else:
        arcpy.AddMessage("Skipping: " + row.ID_NO + "\t" + row.BINOMIAL + " (" + str(i) + " out of " + str(rowCount) + ") (" + str(datetime.datetime.now()) + ")")
    
    
