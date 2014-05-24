import struct, gzip, glob
from gzip import FEXTRA, FNAME
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

files = glob.glob(INPUT_ZIPS + "*.gz")
for file in files:
    f = gzip.open(file)
    print read_gzip_info(f)

