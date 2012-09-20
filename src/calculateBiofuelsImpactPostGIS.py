import psycopg2
from dbconnect import dbconnect
conn = dbconnect('species_dev')
cur = conn.cur
cur.execute("SELECT speciesid FROM biofuels_species")
species = cur.fetchall()
f = open(r"E:\cottaan\My Documents\BiofuelStatsPostGIS.csv", 'a')
for s in species:
    try:        
        #conn.cur.execute("select sum(area) as total_area from (SELECT st_area(st_transform(st_intersection(speciesll.geom,malaysia.geom),3376)) as area FROM speciesll,malaysia  WHERE speciesid='141354' and st_intersects(speciesll.geom,malaysia.geom)='t' and presence in ('Extant', 'Proabably Extant')) as sub")
        conn.cur.execute("select sum(area) as total_area from (SELECT st_area(st_transform(st_intersection(speciesll.geom,malaysia.geom),3376)) as area FROM speciesll,malaysia  WHERE speciesid='" + s[0] + "' and st_intersects(speciesll.geom,malaysia.geom)='t' and presence in ('Extant', 'Proabably Extant')) as sub")
        countryarea = conn.cur.fetchone()[0]
        #conn.cur.execute("select sum(croplandincrease) from (select ((st_area(st_transform(st_intersection(speciesll.geom,biofuels_change_only_grids.geom),3376)) * cropland)/100) as croplandincrease FROM speciesll,biofuels_change_only_grids WHERE speciesid='141354' and st_intersects(speciesll.geom,biofuels_change_only_grids.geom)='t' and presence in ('Extant', 'Proabably Extant')) as sub")
        conn.cur.execute("select sum(croplandincrease) from (select ((st_area(st_transform(st_intersection(speciesll.geom,biofuels_change_only_grids.geom),3376)) * cropland)/100) as croplandincrease FROM speciesll,biofuels_change_only_grids WHERE speciesid='" + s[0] + "' and st_intersects(speciesll.geom,biofuels_change_only_grids.geom)='t' and presence in ('Extant', 'Proabably Extant')) as sub")
        croplandincrease = conn.cur.fetchone()[0]
        f.write(s[0] + "," + str(countryarea) + "," + str(croplandincrease) + "," + str((croplandincrease/countryarea)*100) + "\n")
        print s[0] + "," + str(countryarea) + "," + str(croplandincrease) + "," + str((croplandincrease/countryarea)*100)
    except psycopg2.InternalError as e:
        print s[0] + ": " + str(e.args[0])
    except TypeError as e: #when eithe area is 0 you will get a NoneType 
        print s[0] + ": " + str(e.args[0])
    #break
        
f.close()
