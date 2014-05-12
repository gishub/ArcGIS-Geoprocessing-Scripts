# Iterates through species range data and outputs each unique species to a json file ready for import into Apache Hadoop
# THIS MODULE HAS MEMORY LEAKS IF YOU RUN IT IN ARCGIS - SO RUN AS A PYTHON MODULE - HENCE THE APPEND PATHS STATEMENTS
import sys
sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy')
sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.2\bin')
import  arcpy, zipfile, os

def createSpeciesJson(id, filename):
    arcpy.SelectLayerByAttribute_management(SPECIES_FEATURE_LAYER_NAME, "NEW_SELECTION", "speciesid2=" + str(id))
    try:
        arcpy.FeaturesToJSON_hadoop(SPECIES_FEATURE_LAYER_NAME, OUTPUT_PATH + filename + ".json", "UNENCLOSED_JSON", "FORMATTED")
    except Exception as e:
        print e.message
    zip = zipfile.ZipFile(OUTPUT_PATH + filename + ".zip", "w", zipfile.ZIP_DEFLATED, True)
    zip.write(OUTPUT_PATH + filename + ".json", filename + ".json")
    os.remove(OUTPUT_PATH + filename + ".json")
    zip.close()
    
# CONSTANT DECLARATIONS
SPECIES_TABLE = r"E:\cottaan\My Documents\ArcGIS\jsonToFeaturesOutput\New File Geodatabase.gdb\SpeciesData"
EXTENT_FC = "in_memory\\RangesFC"
OUTPUT_PATH = "E:/cottaan/My Documents/ArcGIS/jsonToFeaturesOutput/zip/"
SPECIES_FEATURE_LAYER_NAME = "AllSpecies"

# INPUT PARAMETERS
arcpy.MakeFeatureLayer_management(r"E:\cottaan\My Documents\ArcGIS\IUCN_species2011.gdb\AllSpecies", SPECIES_FEATURE_LAYER_NAME)
scratchFC = r"E:\cottaan\My Documents\ArcGIS\jsonToFeaturesOutput\New File Geodatabase.gdb\tmp"

# ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.AddToolbox(r"E:\cottaan\My Documents\ArcGIS\Toolboxes\geoprocessing-tools-for-hadoop-master\HadoopTools.pyt")

# CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
print "Creating unique species table"
# arcpy.Frequency_analysis(SPECIES_FEATURE_LAYER_NAME, SPECIES_TABLE, "speciesid2")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

# ITERATE THROUGH THE SPECIES TO OUTPUT THE RASTER FOR EACH ONE
print "Iterating through species"
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.speciesid2    
    if (id != None):  # for some reason a NULL is a space in the FREQUENCY table
        filename = "species" + str(id) 
        if os.path.isfile(OUTPUT_PATH + filename + ".zip"):
            print "File " + OUTPUT_PATH + filename + ".zip already exists - skipping (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")"
        else:
            print "Outputting JSON for species " + str(id) + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")"
            createSpeciesJson(id, filename)
    else:
        print "No species id found (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")"
    counter = counter + 1
