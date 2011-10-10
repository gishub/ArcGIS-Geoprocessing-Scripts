import arcpy
quadkey=arcpy.GetParameterAsText(0)
speciesDataTable=arcpy.GetParameterAsText(1)
arcpy.MakeTableView_management(speciesDataTable,"in_memory\tmpTable","\"quadkey\" like '" + quadkey + "%'")
arcpy.Statistics_analysis("in_memory\tmpTable","tmpTable2","speciesID COUNT","mx;my")
arcpy.AddMessage(arcpy.GetCount_management("tmpTable2"))
