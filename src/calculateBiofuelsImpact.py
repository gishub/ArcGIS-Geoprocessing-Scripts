import arcpy

# Load required toolboxes
arcpy.ImportToolbox("E:/cottaan/My Documents/ArcGIS/Biofuels/Biofuels.gdb/Toolbox")


# Local variables:
species = arcpy.GetParameterAsText(0)
speciesid = arcpy.GetParameterAsText(1)
f = open(r"E:\cottaan\My Documents\ArcGIS\BiofuelStats.csv", 'a')

# Process: Intersect species and grids
arcpy.gp.toolbox = "E:/cottaan/My Documents/ArcGIS/Biofuels/Biofuels.gdb/Toolbox";
# Warning: the toolbox E:/cottaan/My Documents/ArcGIS/Biofuels/Biofuels.gdb/Toolbox DOES NOT have an alias. 
# Please assign this toolbox an alias to avoid tool name collisions
# And replace arcpy.gp.Model(...) with arcpy.Model_ALIAS(...)
results = arcpy.gp.Model(species)
countryarea = float(results.getOutput(0))
croplandincrease = float(results.getOutput(1))
percentImpact = (croplandincrease / countryarea) * 100
arcpy.AddMessage(speciesid + "," + str(countryarea) + "," + str(croplandincrease) + "," + str(percentImpact))
f.write(speciesid + "," + str(countryarea) + "," + str(croplandincrease) + "," + str(percentImpact) + "\n")
f.close()
#arcpy.AddMessage("Country area: " + str(countryarea))
#arcpy.AddMessage("Cropland increase: " + str(croplandincrease))
#arcpy.AddMessage("Percent impact: " + str(percentImpact))
