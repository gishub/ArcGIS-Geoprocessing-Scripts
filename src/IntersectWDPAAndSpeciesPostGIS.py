import psycopg2, gzip, datetime
#DSN = "dbname='dbdopa' user='usrdopa' host='durga.jrc.org' password='W25e12b'"
#DSN = "dbname='dopa' user='arcuser' host='species.jrc.it' password='Cy63rmn'"
DSN = "dbname='dev' user='appuser' host='species.jrc.it' password='5Ti5k9'"

if __name__ == '__main__':
    conn = psycopg2.connect(DSN)
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute("SELECT DISTINCT id_no::int FROM species WHERE id_no != ' '")
    rows = cursor.fetchall()
    count = 1
    f = open(r"E:\cottaan\My Documents\ArcGIS\wdpa_iucn.csv", 'a')
    for row in rows:
#        cursor2.execute("SELECT * FROM species WHERE id_no = '" + str(row[0]) + "'")
        sql = "select distinct species.id_no,wdpaid from wdpa, species where st_intersects(species.geom, wdpa.geom) and species.id_no='" + str(row[0]) + "'"
        print str(datetime.datetime.now()) + "\t" + str(count)+ "\t" + sql
        cursor2.execute(sql)
        species = cursor2.fetchall()
        for s in species:
            f.write(str(s[0]).strip() + "," + str(int(s[1])).strip() + "\n")
        count += 1
#        if count == 40: 
#            break
    f.close()
    cursor2.close()                                                      # close the cursor to get the species
    cursor.close()                                                      # close the cursor to get the species
    conn.close()                                                        # close the connection to the database
