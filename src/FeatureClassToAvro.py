import sys, arcpy
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

# get the feature class
fc = r'E:\cottaan\My Documents\ArcGIS\tmp\Test_FileGDB.gdb\WGS84\Species'

# get the schema
schema = avro.schema.parse(open("species_new.avsc").read())

# open a writer to write the data
writer = DataFileWriter(open("species.avro", "w"), DatumWriter(), schema)

# get the field list for the feature class
fields = arcpy.ListFields(fc)

# get a cursor to the records
cursor = arcpy.SearchCursor(fc)

# iterate through the records and write the dtaa
row = cursor.next()
while row:
    data = {}
    for field in fields:
        if row.getValue(field.name) != None:
            if field.name == "Shape":
                print row.getValue('shape').WKB
#                 data["Shape"] = row.getValue('shape').WKB  #error
#                 data["Shape"] = bytearray()  #error
#                 data["Shape"] = str(bytearray())  #ran
                data["Shape"] = str(row.getValue('shape').WKB)  #error
            else:
                data[field.name] = row.getValue(field.name)
    print data
    writer.append(data)
    row = cursor.next()
    break 
writer.close()
# 
# reader = DataFileReader(open("users.avro", "r"), DatumReader())
# for user in reader:
#     print user
# reader.close()
