import sys
sys.path.append(r"C:\Anaconda\Lib\site-packages")
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
print "Repairing"
schema = avro.schema.parse(open("E:/cottaan/My Documents/iucn_rl_species_2014_2_no_sens.avsc").read())
writer = DataFileWriter(open("E:/cottaan/My Documents/iucn_rl_species_2014_2_no_sens_repaired.avro", "w"), DatumWriter(), schema)
reader = DataFileReader(open("E:/cottaan/My Documents/iucn_rl_species_2014_2_no_sens.avro", "r"), DatumReader())
for row in reader:
    writer.append(row)
reader.close()
writer.close()