import arcpy
#CONSTANT DECLARATIONS
SPECIES_TABLE = "SpeciesData"
INTERSECTION_TABLE = "intersectionsTable"
scratchFC = "in_memory\\intersecting"

#INPUT PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
paFL = arcpy.GetParameterAsText(1)
#outputTable = arcpy.GetParameterAsText(2)
#if arcpy.Exists(outputTable):
#    arcpy.Delete_management(outputTable)
    
#CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "ID_NO")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

#CREATE A TABLE TO HOLD THE SPECIES/PA INTERSECTIONS
arcpy.AddMessage("Creating intersections table")
arcpy.CreateTable_management(r"E:\cottaan\My Documents\ArcGIS\Default.gdb","intersections")
arcpy.MakeTableView_management(r"E:\cottaan\My Documents\ArcGIS\Default.gdb\intersections",INTERSECTION_TABLE)
arcpy.AddMessage("Adding spID field")
arcpy.AddField_management(INTERSECTION_TABLE,"spID","LONG")
arcpy.AddMessage("Adding wdpaid field")
arcpy.AddField_management(INTERSECTION_TABLE,"wdpaid","LONG")

#ITERATE THROUGH THE SPECIES TO OVERLAY THE PAS FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Species ID:" + id + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
        arcpy.AddMessage("Selecting species")
        arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "ID_NO='" + id + "'")
        arcpy.AddMessage("Selecting PAs")
        arcpy.SelectLayerByLocation_management(paFL,"INTERSECT",speciesFL)
        arcpy.AddMessage("Copying PAs")
        arcpy.CopyFeatures_management(paFL, scratchFC)
        rows = arcpy.SearchCursor(scratchFC) 
        insertrows = arcpy.InsertCursor(INTERSECTION_TABLE)
        for row in rows: 
            insertrow = insertrows.newRow() 
            insertrow.spID = int(id) 
            insertrow.wdpaid = int(row.wdpaid) 
            insertrows.insertRow(insertrow)             
#            arcpy.AddMessage(str(int(row.wdpaid)) + " " + id);
        arcpy.Delete_management(scratchFC)
        counter = counter + 1