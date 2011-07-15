import arcpy

def getSnapMetres(coord,up):
    if (up==True):
        return (((int(coord/1000))+1)*1000)
    else:
        return (((int(coord/1000))-1)*1000)

#CONSTANT DECLARATIONS
PRIORITY_FIELDNAME = "Priority"
ALL_SPECIES_FC = "Ranges"
SPECIES_TABLE = "SpeciesData"
EXTENT_FC = "in_memory\\RangesFC"

#INPUT PARAMETERS
speciesFCPath = arcpy.GetParameterAsText(0)
rasterWorkspace = arcpy.GetParameter(1)
scratchFC = str(rasterWorkspace) + "\\tmp"

#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True

#ADD THE PRIORITY FIELD IF IT IS NOT ALREADY PRESENT
if (len(arcpy.ListFields(speciesFCPath, PRIORITY_FIELDNAME))==0):
    arcpy.AddMessage("Adding priority field to species feature class")
    arcpy.AddField_management(speciesFCPath, PRIORITY_FIELDNAME,"LONG")
    arcpy.AddMessage("Populating priority field")
    arcpy.CalculateField_management(speciesFCPath, PRIORITY_FIELDNAME,1)
    
#CREATE AN IN-MEMORY FC OF THE SPECIES
arcpy.AddMessage("Creating Feature Layer for all species")
arcpy.MakeFeatureLayer_management(speciesFCPath, ALL_SPECIES_FC)

#CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(ALL_SPECIES_FC, SPECIES_TABLE, "ID_NO")
#arcpy.MakeTableView_management(r"C:\Users\AndrewCottam\Documents\ArcGIS\Default.gdb\SpeciesTable",SPECIES_TABLE)

#ITERATE THROUGH THE SPECIES TO OUTPUT THE RASTER FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Species ID:" + id)
        arcpy.AddMessage("Selecting features")
#        arcpy.MakeFeatureLayer_management(ALL_SPECIES_FC, SPECIES_FC, "ID_NO='" + id + "'")        
        arcpy.SelectLayerByAttribute_management(ALL_SPECIES_FC, "NEW_SELECTION", "ID_NO='" + id + "'")
        arcpy.AddMessage("Copying features")
        arcpy.CopyFeatures_management(ALL_SPECIES_FC, scratchFC)
        count = arcpy.GetCount_management(scratchFC)
        arcpy.AddMessage("Getting extent")
        if (count==1):
            features = arcpy.SearchCursor(scratchFC, "ID_NO='" + id + "'")
            for feature in features:
                geometry = feature.Shape
                extent = geometry.Extent
            del features
        else:    
            arcpy.MinimumBoundingGeometry_management(scratchFC, EXTENT_FC, "ENVELOPE", "ALL")
            dsc = arcpy.Describe(EXTENT_FC)
            extent = dsc.Extent    
            arcpy.Delete_management(EXTENT_FC)
        arcpy.AddMessage("Calculating raster extent")
        minx = getSnapMetres(extent.XMin, False)
        maxx = getSnapMetres(extent.XMax, True)
        miny = getSnapMetres(extent.YMin, False)
        maxy = getSnapMetres(extent.YMax, True)
        arcpy.AddMessage("minx:" + str(minx))
        arcpy.AddMessage("maxx:" + str(maxx))
        arcpy.AddMessage("miny:" + str(miny))
        arcpy.AddMessage("maxy:" + str(maxy))
        arcpy.AddMessage("Creating raster" + str(rasterWorkspace) + "\\ID" + id)
        arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)
        arcpy.PolygonToRaster_conversion(scratchFC, "ID_NO", str(rasterWorkspace) + "\\ID" + id, "MAXIMUM_AREA", PRIORITY_FIELDNAME, 1000)