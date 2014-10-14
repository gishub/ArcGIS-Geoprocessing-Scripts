import sys, arcpy, json
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
from StringIO import StringIO

# get the feature class
fc = r'E:\cottaan\My Documents\ArcGIS\iucn_rl_species_2014_2.gdb\wdpa_aug14_100km2_moll'
desc = arcpy.Describe(fc)

# get the field list for the feature class
fields = arcpy.ListFields(fc)
fieldsArray = []
for field in fields:
    if field.type == "OID":
        fieldType = 'long'
    elif field.type == "Geometry":
        fieldType = 'bytes'
    else:
        fieldType = field.type.lower()
    if field.isNullable:
        fieldsArray.append({"name": field.name, "type": [fieldType, "null"]})
    else:
        fieldsArray.append({"name": field.name, "type": fieldType})

# create the schema from the fields
schemajson = {"type": "record", "name": desc.name, "fields": fieldsArray }
schema = avro.schema.parse(json.dumps(schemajson, None))
print "Schema created"

# open a writer to write the data
writer = DataFileWriter(open("E:/cottaan/My Documents/" + desc.name + ".avro", "w"), DatumWriter(), schema)
 
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
            if field.name.lower() == "shape":
                data[field.name] = str(row.getValue(field.name).WKB)  
            else:
                data[field.name] = row.getValue(field.name)
    writer.append(data)
    row = cursor.next()
    count = count + 1
writer.close()
print "Data written to " + desc.name + ".avro"