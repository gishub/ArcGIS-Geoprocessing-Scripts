import arcpy
#CONSTANT DECLARATIONS
ALL_SPECIES_FC = "Ranges"
SPECIES_TABLE = "SpeciesData"
INTERSECTION_FC = "in_memory\\intersection"
scratchFC = r"E:\cottaan\My Documents\ArcGIS\scratchFC.shp"

#INPUT PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
paFL = arcpy.GetParameterAsText(1)
outputWorkspace = arcpy.GetParameterAsText(2)
singleOutputFC = arcpy.GetParameter(3) #1 to use separate FC for each species
outputFC = outputWorkspace + "\\intersections"
outputFCList = []
if arcpy.Exists(outputFC):
    arcpy.Delete_management(outputFC)
    
#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"

#CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "ID_NO")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

#ITERATE THROUGH THE SPECIES TO OVERLAY THE PAS FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Species ID:" + id + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
#        arcpy.AddMessage("Selecting features")
        arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "ID_NO='" + id + "'")
#        arcpy.AddMessage("Copying features")
        arcpy.CopyFeatures_management(speciesFL, scratchFC)
#        arcpy.AddMessage("Intersecting features")
        arcpy.Intersect_analysis([scratchFC,paFL],INTERSECTION_FC)
        if (singleOutputFC==1):
            if arcpy.Exists(outputFC):
                arcpy.AddMessage("Appending features to output feature class")
                arcpy.Append_management(INTERSECTION_FC,outputFC)
            else:
                arcpy.AddMessage("Creating output feature class")
                arcpy.CopyFeatures_management(INTERSECTION_FC,outputFC)
        else:
            outputFC = outputWorkspace + "\\I" + id
            arcpy.CopyFeatures_management(INTERSECTION_FC,outputFC)  
            outputFCList.append(outputFC)             
        arcpy.Delete_management(scratchFC)
        counter = counter + 1
if (singleOutputFC==0):
    arcpy.AddMessage("Merging feature classes " + "(" + str(datetime.datetime.now()) + ")")
    arcpy.Merge_management(outputFCList,outputWorkspace + "\\intersections")
    arcpy.AddMessage("Deleting temporary feature classes " + "(" + str(datetime.datetime.now()) + ")")
    for item in outputFCList:
        arcpy.Delete_management(item)