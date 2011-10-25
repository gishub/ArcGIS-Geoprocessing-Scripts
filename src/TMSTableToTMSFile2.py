#This uses psycopg2 to access the Postgresql database rather than the esri cursor on a file gdb table
import psycopg2
import cPickle
conn = psycopg2.connect(host="damon.jrc.it", database="dbespecies", user="usrespecies", password="gem2011")
cur = conn.cursor()
cur.execute("SELECT tx,ty,count FROM public.pilotspeciesdatastatistics WHERE tx>27400 and tx<27500 and ty>16900 and ty<17000")
rows=cur.fetchall()
records=numpy.transpose(numpy.array(rows))
f = open(r"D:\GIS Data\Andrew\SpeciesRichness.npy",'wb')
cPickle.dump(records, f, protocol=2)
f.close()