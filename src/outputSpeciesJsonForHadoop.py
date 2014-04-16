import arcpy, zipfile, os

# CONSTANT DECLARATIONS
SPECIES_TABLE = "SpeciesData"
EXTENT_FC = "in_memory\\RangesFC"
OUTPUT_PATH = "E:/cottaan/My Documents/ArcGIS/jsonToFeaturesOutput/"

# INPUT PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
scratchFC = r"E:\cottaan\My Documents\ArcGIS\jsonToFeaturesOutput\New File Geodatabase.gdb\tmp"

# ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.AddToolbox(r"E:\cottaan\My Documents\ArcGIS\Toolboxes\geoprocessing-tools-for-hadoop-master\HadoopTools.pyt")

# CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "ID_NO")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

# ITERATE THROUGH THE SPECIES TO OUTPUT THE RASTER FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id != " "):  # for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Outputting JSON for species " + id + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
        arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "ID_NO='" + id + "'")
        arcpy.CopyFeatures_management(speciesFL, scratchFC)
        filename = "species" + str(id) 
        arcpy.FeaturesToJSON_hadoop(scratchFC, OUTPUT_PATH + filename + ".json", "UNENCLOSED_JSON", "FORMATTED")
        zip = zipfile.ZipFile(OUTPUT_PATH + filename + ".zip", "w", zipfile.ZIP_DEFLATED, True)
        zip.write(OUTPUT_PATH + filename + ".json", filename + ".json")
        zip.close()
        os.remove(OUTPUT_PATH + filename + ".json")
        arcpy.Delete_management(scratchFC)
    else:
        arcpy.AddMessage("No species id found (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
    counter = counter + 1
