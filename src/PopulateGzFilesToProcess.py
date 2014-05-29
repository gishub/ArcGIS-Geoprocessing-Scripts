import win32com.client, struct, gzip, glob, logging
from gzip import FEXTRA, FNAME, os
INPUT_ZIPS = "D:/Users/andrewcottam/Documents/ArcGIS/fao/Input Zips/"
# INPUT_ZIPS = "/Users/andrewcottam/Desktop/"

def read_gzip_info(gzipfile):
    gf = gzipfile.fileobj
    pos = gf.tell()
    # Read archive size
    gf.seek(-4, 2)
    size = struct.unpack('<I', gf.read())[0]
    gf.seek(0)
    magic = gf.read(2)
    if magic != '\037\213':
        raise IOError, 'Not a gzipped file'
    method, flag, mtime = struct.unpack("<BBIxx", gf.read(8))
    if not flag & FNAME:
        # Not stored in the header, use the filename sans .gz
        gf.seek(pos)
        fname = gzipfile.name
        if fname.endswith('.gz'):
            fname = fname[:-3]
        return fname, size
    if flag & FEXTRA:
        # Read & discard the extra field, if present
        gf.read(struct.unpack("<H", gf.read(2)))
    # Read a null-terminated string containing the filename
    fname = []
    while True:
        s = gf.read(1)
        if not s or s == '\000':
            break
        fname.append(s)
    gf.seek(pos)
    return ''.join(fname), size

logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\OutputFTPStatistics.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
engine = win32com.client.Dispatch('DAO.DBEngine.120')
db = engine.OpenDatabase('D:/Users/andrewcottam/Documents/fao_ftp_files.accdb')
q = db.CreateQueryDef("","DELETE DownloadedZipFiles.* FROM DownloadedZipFiles;")
q.Execute()
queryDef = db.CreateQueryDef("", "select *from DownloadedZipFiles")
r = queryDef.OpenRecordset()
files = glob.glob(INPUT_ZIPS + "*.gz")
total = len(files)
counter = 1
for file in files:
    filename = os.path.basename(file)
    filesize = os.path.getsize(file)
    print "processing " + filename + " (" + str(counter) + "/" + str(total) + ")"
    if filesize == 0:
        print filename + " has a file size of 0 bytes"
        logging.error(filename + " has a file size of 0 bytes")
        archivename, archivesize = "", 0
    else:
        f = gzip.open(file)
        archivename, archivesize = read_gzip_info(f)
    try:
        r.AddNew()
        r.Fields['fullpath'] = file
        r.fields['filename'] = filename
        r.fields['filesize'] = float(filesize) #must explicitly case to a float otherwise it passes as an int and gives errors
        r.fields['archivename'] = archivename
        r.fields['archivesize'] = float(archivesize)
        r.Update()
        counter = counter + 1
    except (Exception)as e:
        print e
        logging.error("Error on file " + filename + " filesize: " + str(filesize) + " archivename: " + archivename + " archivesize: " + str(archivesize))
        pass
db.QueryDefs("UpdateOutputZipFiles").Execute()
q = db.CreateQueryDef("","UPDATE DownloadedZipFiles INNER JOIN ftp_files ON DownloadedZipFiles.filename = ftp_files.filename SET DownloadedZipFiles.ftpurl = [fullfilename];")
q.Execute()
db.Close()
