import sys, arcpy, json
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, SchemaResolutionException
from datetime import date
USE_WKB = False  # set to true to encode using well-known binary
# get the feature class
# fc = r'E:\cottaan\My Documents\ArcGIS\iucn_rl_species_2014_2.gdb\wdpa_latest_14_10_14'
# fc = r'E:\cottaan\My Documents\ArcGIS\iucn_rl_species_2014_2.gdb\iucn_rl_species_2014_2_no_sens'
fc = r'E:\export\iucn_rl_species_2014_2.gdb\iucn_rl_species_2014_2_no_sens'
desc = arcpy.Describe(fc)
# outputfilePrefix = "E:/cottaan/My Documents/" + desc.name
outputfilePrefix = "C:/Users/cottaan/Documents/" + desc.name

# get the field list for the feature class
fields_unfiltered = arcpy.ListFields(fc)
fieldnames_species = ['shape','OBJECTID','id_no','binomial','presence','origin','compiler','year','citation','source','dist_comm','island','subspecies','subpop','data_sens','sens_comm','legend','seasonal','owner','ecosystem','areakm2','taxonid','subpop_id','rl_update','rl_update_notes','rl_update_date','tax_comm','assessmentid_pp']
# fieldnames_species = ['shape']
for i in range(len(fieldnames_species)):
    outputfilePrefix = "C:/Users/cottaan/Documents/" + desc.name + "_" + str(i)

    fields = [f for f in fields_unfiltered if f.name in fieldnames_species[:i + 1]]
    print "\nCreating an avro file with the following names: " + ",".join([f.name for f in fields])
    fieldsArray = []
    # fieldsArray.append({'name' : 'shape', 'type':'string'})
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
    writer = DataFileWriter(open(outputfilePrefix + ".avro", "w"), DatumWriter(), schema)
     
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
                if field.name.lower() in ["shape", "geom"]:
                    if USE_WKB:
                        data[field.name] = str(row.getValue(field.name).WKB)
                    else:
                        data[field.name] = row.getValue(field.name).WKT  
                elif field.type == "Date":
                    data[field.name] = date.isoformat(row.getValue(field.name))
                else:
                    data[field.name] = row.getValue(field.name)
        writer.append(data)
    #     print data['OBJECTID']
        row = cursor.next()
        count = count + 1
        if count == 14:
            break
    writer.close()
    print "Data written to " + outputfilePrefix + ".avro"
    print "\nChecking file.."
    reader = DataFileReader(open(outputfilePrefix + ".avro", "r"), DatumReader())
    for record in reader:
        print record
    reader.close()
    print "Finished" 