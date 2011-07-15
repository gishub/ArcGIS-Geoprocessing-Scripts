'''
Created on Jul 14, 2011

@author: AndrewCottam
'''
import arcpy
def getSnapMetres(coord,up):
    if (up==True):
        return (((int(coord/1000))+1)*1000)
    else:
        return (((int(coord/1000))-1)*1000)
#TODO: Add in the code to add a Priority field and populate it with 1s
print "Creating Feature Layer for all species"
arcpy.MakeFeatureLayer_management(r"D:\GIS Data\IUCN\OverlayAnalysis.gdb\Species", "Ranges")
print "Creating unique species table"
#arcpy.Frequency_analysis("Ranges", "SpeciesTable", "ID_NO")
arcpy.MakeTableView_management(r"C:\Users\AndrewCottam\Documents\ArcGIS\Default.gdb\SpeciesTable","SpeciesData")
AllSpecies = arcpy.SearchCursor("SpeciesData")
print ("Iterating through species")
for species in AllSpecies:
    id = species.ID_NO    
    if (id!=" "):# for some reason a NULL is a space in the FREQUENCY table
        print "Species ID:" + id
        arcpy.AddMessage("Species ID:" + id)
        arcpy.MakeFeatureLayer_management("Ranges", "SpeciesLayer", "ID_NO='" + id + "'")
        count = arcpy.GetCount_management("SpeciesLayer")
        if (count==1):
            features = arcpy.SearchCursor("SpeciesLayer","ID_NO='" + id + "'")
            for feature in features:
                geometry = feature.Shape
                extent = geometry.Extent
            del features
        else:    
            arcpy.MinimumBoundingGeometry_management("SpeciesLayer", "in_memory\\RangesFC","ENVELOPE","ALL")
            dsc = arcpy.Describe("in_memory\RangesFC")
            extent = dsc.Extent    
            arcpy.Delete_management("in_memory\\RangesFC")
            minx = getSnapMetres(extent.XMin,False)
            maxx = getSnapMetres(extent.XMax,True)
            miny = getSnapMetres(extent.YMin,False)
            maxy = getSnapMetres(extent.YMax,True)
            print "minx:" + str(minx)
            print "maxx:" + str(maxx)
            print "miny:" + str(miny)
            print "maxy:" + str(maxy)
            arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)
            arcpy.PolygonToRaster_conversion("SpeciesLayer", "ID_NO", r"D:\GIS Data\Andrew\MapperDemo.gdb\ID" + id, "MAXIMUM_AREA", "Priority", 1000)
            arcpy.Delete_management("SpeciesLayer")
            
print "End"
        