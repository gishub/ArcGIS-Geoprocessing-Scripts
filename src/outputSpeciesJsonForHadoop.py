import arcpy, zipfile, os

# CONSTANT DECLARATIONS
SPECIES_TABLE = "SpeciesData"
EXTENT_FC = "in_memory\\RangesFC"
OUTPUT_PATH = "E:/cottaan/My Documents/ArcGIS/jsonToFeaturesOutput/zip/"

# INPUT PARAMETERS
speciesFL = arcpy.GetParameterAsText(0)
scratchFC = r"E:\cottaan\My Documents\ArcGIS\jsonToFeaturesOutput\New File Geodatabase.gdb\tmp"

# ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.AddToolbox(r"E:\cottaan\My Documents\ArcGIS\Toolboxes\geoprocessing-tools-for-hadoop-master\HadoopTools.pyt")

# CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "speciesid2")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

# ITERATE THROUGH THE SPECIES TO OUTPUT THE RASTER FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.speciesid2    
    if (id != None):  # for some reason a NULL is a space in the FREQUENCY table
        filename = "species" + str(id) 
        if os.path.isfile(OUTPUT_PATH + filename + ".zip"):
            arcpy.AddMessage("File " + OUTPUT_PATH + filename + ".zip already exists - skipping (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
        else:
            arcpy.AddMessage("Outputting JSON for species " + str(id) + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
            arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "speciesid2=" + str(id))
            arcpy.CopyFeatures_management(speciesFL, scratchFC)
            try:
                arcpy.FeaturesToJSON_hadoop(scratchFC, OUTPUT_PATH + filename + ".json", "UNENCLOSED_JSON", "FORMATTED")
            except Exception as e:
                arcpy.AddError(e.message)
            zip = zipfile.ZipFile(OUTPUT_PATH + filename + ".zip", "w", zipfile.ZIP_DEFLATED, True)
            zip.write(OUTPUT_PATH + filename + ".json", filename + ".json")
            zip.close()
            del zip
            os.remove(OUTPUT_PATH + filename + ".json")
    else:
        arcpy.AddMessage("No species id found (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
    counter = counter + 1