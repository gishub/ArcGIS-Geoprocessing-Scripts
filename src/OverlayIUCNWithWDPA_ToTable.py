import arcpy
#CONSTANT DECLARATIONS
ALL_SPECIES_FC = "Ranges"
SPECIES_TABLE = "SpeciesData"
SCRATCH_FC = "in_memory\\scratch"
INTERSECTION_FC = "intersection"
FREQUENCY_TABLE = "in_memory\\frequency"
OUTPUT_TABLE_NAME = "intersections"

#INPUT PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
paFL = arcpy.GetParameterAsText(1)
outputWorkspace = arcpy.GetParameterAsText(2)
outputTable = outputWorkspace + "\\" + OUTPUT_TABLE_NAME
if arcpy.Exists(outputTable):
    arcpy.Delete_management(outputTable)
    
#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"

#CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "ID_NO")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

#CREATE A TABLE THAT WILL PUT THE INTERSECT DATA IN
arcpy.CreateTable_management(outputWorkspace,OUTPUT_TABLE_NAME)
arcpy.AddField_management(OUTPUT_TABLE_NAME,"ID_NO","TEXT")
arcpy.AddField_management(OUTPUT_TABLE_NAME,"wdpaid","LONG")
arcpy.AddField_management(OUTPUT_TABLE_NAME,"SHAPE_Area","DOUBLE")

#ITERATE THROUGH THE SPECIES TO OVERLAY THE PAS FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Species ID:" + id + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
        arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "ID_NO='" + id + "'")
        arcpy.CopyFeatures_management(speciesFL, SCRATCH_FC)
        arcpy.Intersect_analysis([SCRATCH_FC,paFL],INTERSECTION_FC)
        arcpy.Frequency_analysis(INTERSECTION_FC,FREQUENCY_TABLE,["wdpaid","ID_NO"],"SHAPE_Area")
        arcpy.AddMessage("Appending features to output table")
        arcpy.Append_management(FREQUENCY_TABLE,outputTable,"NO_TEST")
        arcpy.Delete_management(SCRATCH_FC)
        arcpy.Delete_management(INTERSECTION_FC)
        arcpy.Delete_management(FREQUENCY_TABLE)    
    counter = counter + 1        