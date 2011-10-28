#This uses psycopg2 to access the Postgresql database rather than the esri cursor on a file gdb table
import psycopg2
import cPickle
import numpy
import arcpy
speciesID=arcpy.GetParameterAsText(0)
conn = psycopg2.connect(host="durga.jrc.org", database="dbdopa", user="usrdopa", password="W25e12b")
cur = conn.cursor()
cur.execute("SELECT tx,ty,z FROM public.pilotspeciesdata WHERE speciesid='" + speciesID + "'")
rows=cur.fetchall()
records=numpy.transpose(numpy.array(rows))
records=numpy.reshape(records,len(records[0])*3) #convert the arraytx,arrayty,arrayz to a single array
f = open(r"E:\cottaan\My Documents\ArcGIS\ID" + speciesID + ".npy",'wb')
#f = open("/srv/www/htdocs/eSpecies/SpeciesRichness.npy",'wb')
cPickle.dump(records, f, protocol=2)
f.close()