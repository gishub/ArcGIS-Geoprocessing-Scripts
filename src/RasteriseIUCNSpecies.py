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
speciesFL = arcpy.GetParameterAsText(0)
rasterWorkspace = arcpy.GetParameter(1)
scratchFC = r"E:\cottaan\My Documents\ArcGIS\tmp.shp"

#ENVIRONMENT VARIABLES
arcpy.env.overwriteOutput = True
arcpy.env.rasterStatistics = None
arcpy.env.outputCoordinateSystem = "Coordinate Systems/Projected Coordinate Systems/World/WGS 1984 Web Mercator.prj"
arcpy.env.compression = "PackBits"

#ADD THE PRIORITY FIELD IF IT IS NOT ALREADY PRESENT
if (len(arcpy.ListFields(speciesFL, PRIORITY_FIELDNAME))==0):
    arcpy.AddMessage("Adding priority field to species feature class")
    arcpy.AddField_management(speciesFL, PRIORITY_FIELDNAME,"LONG")
    arcpy.AddMessage("Populating priority field")
    arcpy.CalculateField_management(speciesFCPath, PRIORITY_FIELDNAME,1)
    
#CREATE A TABLE OF UNIQUE SPECIES TO ITERATE THROUGH
arcpy.AddMessage("Creating unique species table")
arcpy.Frequency_analysis(speciesFL, SPECIES_TABLE, "ID_NO")
count = str(arcpy.GetCount_management(SPECIES_TABLE))
counter = 1

#ITERATE THROUGH THE SPECIES TO OUTPUT THE RASTER FOR EACH ONE
arcpy.AddMessage("Iterating through species")
AllSpecies = arcpy.SearchCursor(SPECIES_TABLE)
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        arcpy.AddMessage("Species ID:" + id + " (" + str(counter) + " of " + count + ") (" + str(datetime.datetime.now()) + ")")
        arcpy.SelectLayerByAttribute_management(speciesFL, "NEW_SELECTION", "ID_NO='" + id + "'")
        arcpy.CopyFeatures_management(speciesFL, scratchFC)
        count2 = arcpy.GetCount_management(scratchFC)
        if (count2==1):
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
        arcpy.AddMessage("Raster extent:")
        minx = getSnapMetres(extent.XMin, False)
        maxx = getSnapMetres(extent.XMax, True)
        miny = getSnapMetres(extent.YMin, False)
        maxy = getSnapMetres(extent.YMax, True)
        arcpy.AddMessage("minx:" + str(minx))
        arcpy.AddMessage("maxx:" + str(maxx))
        arcpy.AddMessage("miny:" + str(miny))
        arcpy.AddMessage("maxy:" + str(maxy))
        arcpy.AddMessage("Creating raster: " + str(rasterWorkspace) + "\\ID" + id)
        arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)
        arcpy.PolygonToRaster_conversion(scratchFC, "ID_NO", str(rasterWorkspace) + "\\ID" + id, "MAXIMUM_AREA", PRIORITY_FIELDNAME, 1000)
        arcpy.env.extent = None #Reset the extent
        arcpy.Delete_management(scratchFC)
        counter = counter + 1