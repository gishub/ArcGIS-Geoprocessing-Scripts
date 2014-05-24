import struct,gzip
from gzip import FEXTRA, FNAME

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
        if not s or s=='\000':
            break
        fname.append(s)

    gf.seek(pos)
    return ''.join(fname), size

f = gzip.open("/Users/andrewcottam/Desktop/ClimAf_1_1961_2099_lpjm_can_wfdei_cord_B1_harea_sea_teco_ir.nc.gz")
print read_gzip_info(f)
