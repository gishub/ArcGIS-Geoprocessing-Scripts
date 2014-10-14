import sys, arcpy
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

# get the feature class
# fc = r'E:\cottaan\My Documents\ArcGIS\tmp\Test_FileGDB.gdb\WGS84\Species'
fc = r'E:\cottaan\My Documents\ArcGIS\iucn_rl_species_2014_2.gdb\iucn_rl_species_2014_2_no_sens_mollweide'

# get the schema
schema = avro.schema.parse(open("species_2014.avsc").read())

# open a writer to write the data
writer = DataFileWriter(open("species.avro", "w"), DatumWriter(), schema)

# get the field list for the feature class
fields = arcpy.ListFields(fc)

# get a cursor to the records
cursor = arcpy.SearchCursor(fc)

# get the count
total = str(arcpy.GetCount_management(fc))

# iterate through the records and write the dtaa
row = cursor.next()
count = 1
while row:
    print "Processing " + str(count) + " of " + str(total) + " rows"
    data = {}
    for field in fields:
        if row.getValue(field.name) != None:
            if field.name == "shape":
                data["shape"] = str(row.getValue('shape').WKB)  
            else:
                if field.name.upper() in ["OBJECTID","ID_NO","BINOMIAL","PRESENCE","ORIGIN","COMPILER","YEAR","CITATION","SOURCE","DIST_COMM","ISLAND","SUBSPECIES","SUBPOP","TAX_COMMEN","DATA_SENS","SENS_COMM","LEGEND","SEASONAL","OWNER","SPECIESID","ECOSYSTEM"]:
                    data[field.name] = row.getValue(field.name)
    writer.append(data)
    row = cursor.next()
    count = count + 1
    break 
writer.close()
# 
# reader = DataFileReader(open("users.avro", "r"), DatumReader())
# for user in reader:
#     print user
# reader.close()
