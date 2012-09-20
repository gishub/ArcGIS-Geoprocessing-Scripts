import sys
import psycopg2

connectionDSN = {
    # add connection paramters below, suggestion using a dbserver_dbname key
    'durga_dopa':"dbname='dbdopa' user='usrdopa' host='durga.jrc.org' password='W25e12b'" \
    ,'damon_species':"dbname='dbespecies' user='usrespecies' host='damon.jrc.it' password='gem2011'" \
    ,'species_dev':"dbname='dev' user='appuser' host='species.jrc.it' password='5Ti5k9'"
}

class dbconnect:
    """ utility module to connect to PG DBs:
    
    Use like this:

>>> from dbconnect import dbconnect
>>> p = dbconnect('species_dev')
>>> p.cur.execute("select max(speciesid) from species")
>>> p.cur.fetchall()
[('9997',)]
>>> del(p)
    
    """
    
    def __init__(self,DSN=None):
        # the actual connection
        self.conn = None
        
        # the cursor, if available
        self.cur = None
        
        # available connection strings
        self.connections = connectionDSN
        
        if DSN:
            self.open(DSN)        

    def open(self, DSN=connectionDSN['durga_dopa']):  
        """ return a cursor to a PG database """
        try:
            if self.connections.has_key(DSN):
                self.conn = psycopg2.connect(self.connections[DSN])
            else:
                self.conn = psycopg2.connect(DSN)
                
            self.conn.set_isolation_level(0)
    #        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.conn.cursor()
            #return self.cur 
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            # Exit the script and print an error telling what happened.
            raise Exceptions.NoApplicableCode("Database connection failed!\n ->%s" % (exceptionValue))
        
    def close(self):
        """ disconnect from the DB server """
        if self.cur and not self.cur.closed:
            self.cur.close()
            self.cur = None
        
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """ disconnect before deletion """
        self.close() 