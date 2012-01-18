import arcpy
arcpy.AddMessage("Creating intersections table")
outputTable = arcpy.CreateTable_management(r"E:\cottaan\My Documents\ArcGIS\Default.gdb","Africa_Species_PA_Intersections")
arcpy.AddField_management(outputTable,"ID_NO","TEXT")
arcpy.AddField_management(outputTable,"wdpaid","LONG")
insertCursor = arcpy.InsertCursor(r"E:\cottaan\My Documents\ArcGIS\Default.gdb\Africa_Species_PA_Intersections")
rows = arcpy.SearchCursor("African_Species2011")
rowCount = arcpy.GetCount_management("African_Species2011")
i=0
for row in rows:
    i=i+1
    arcpy.SelectLayerByAttribute_management("African_Species2011","NEW_SELECTION","ID_NO='" + row.ID_NO + "'")
    arcpy.SelectLayerByLocation_management("African_Protected_Areas","INTERSECT","African_Species2011")
    paCursor = arcpy.SearchCursor("African_Protected_Areas")
    for pa in paCursor:
        newRow = insertCursor.newRow()
        newRow.ID_NO = row.ID_NO
        newRow.wdpaid = pa.wdpaid
        insertCursor.insertRow(newRow)
    del newRow
    arcpy.AddMessage(row.ID_NO + "\t" + row.BINOMIAL + " (" + str(i) + " out of " + str(rowCount) + ") (" + str(datetime.datetime.now()) + ")")
    
    