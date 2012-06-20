#This uses psycopg2 to access the Postgresql database rather than the esri cursor on a file gdb table
import cPickle
import numpy
import arcpy
from dbconnect import dbconnect
speciesID=arcpy.GetParameterAsText(0)
conn = dbconnect('durga_dopa')
cur = conn.cur
cur.execute("SELECT tx,ty,z FROM public.pilotspeciesdata WHERE speciesid='" + speciesID + "'")
rows=cur.fetchall()
records=numpy.transpose(numpy.array(rows,dtype="int32"))
records=numpy.reshape(records,len(records[0])*3) #convert the arraytx,arrayty,arrayz to a single array
f = open(r"E:\cottaan\My Documents\ArcGIS\ID" + speciesID + ".npy",'wb')
#f = open("/srv/www/htdocs/eSpecies/SpeciesRichness.npy",'wb')
cPickle.dump(records, f, protocol=2)
f.close()