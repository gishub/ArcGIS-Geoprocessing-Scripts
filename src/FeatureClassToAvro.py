import sys, arcpy, json
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, SchemaResolutionException
from datetime import date
USE_WKB = True  # set to true to encode using well-known binary
# get the feature class
fc = r'E:\export\iucn_rl_species_2014_2.gdb\iucn_rl_species_2014_2_no_sens'
fc = r'E:\cottaan\My Documents\ArcGIS\iucn_rl_species_2014_2.gdb\iucn_rl_species_2014_2_no_sens'
fc=r'E:\export\wdpa_latest_14_10_14.gdb\wdpa_latest_14_10_14'
desc = arcpy.Describe(fc)
outputfilePrefix = "E:/export/" + desc.name

# get the field list for the feature class
fields = arcpy.ListFields(fc)
fieldsArray = []
for field in fields:
    if field.type in ["OID"]:
        fieldType = 'long'
    elif field.type in ["SmallInteger", "Integer"]:
        fieldType = 'int'
    elif field.type == "Geometry":
        if USE_WKB:
            fieldType = 'bytes'
        else:
            fieldType = 'string'
    elif field.type == "Date":
        fieldType = 'string'
    else:
        fieldType = field.type.lower()
    if field.isNullable:
        fieldsArray.append({"name": field.name, "type": [fieldType, "null"]})
    else:
        fieldsArray.append({"name": field.name, "type": fieldType})

# create the schema from the fields
schemajson = {"type": "record", "name": desc.name, "fields": fieldsArray }
schemajsonstr = json.dumps(schemajson, None)
f = open(outputfilePrefix + ".avsc", "w")
f.write(schemajsonstr)
f.close()
schema = avro.schema.parse(schemajsonstr)
print "Schema written to " + outputfilePrefix + ".avsc"

# open a writer to write the data
writer = DataFileWriter(open(outputfilePrefix + ".avro", "wb"), DatumWriter(), schema, "deflate")
 
# get a cursor to the records
cursor = arcpy.SearchCursor(fc)
 
# get the count
total = str(arcpy.GetCount_management(fc))
 
# iterate through the records and write the dtaa
row = cursor.next()
count = 0
while row:
    print "Processing " + str(count) + " of " + str(total) + " rows"  
    data = {}
    for field in fields:
        if row.getValue(field.name) != None:
            if field.name.lower() in ["shape", "geom"]:
                if USE_WKB:
                    data[field.name] = bytes(row.getValue(field.name).WKB)
                else:
                    data[field.name] = row.getValue(field.name).WKT  
            elif field.type == "Date":
                data[field.name] = date.isoformat(row.getValue(field.name))
            else:
                data[field.name] = row.getValue(field.name)
    writer.append(data)
    row = cursor.next()
    count = count + 1
    if count == 100:
        break
writer.close()
print "Data written to " + outputfilePrefix + ".avro"
print "\nChecking file.."
reader = DataFileReader(open(outputfilePrefix + ".avro", "rb"), DatumReader())
for record in reader:
    print record['wdpa_id']
reader.close()
print "Finished" 
