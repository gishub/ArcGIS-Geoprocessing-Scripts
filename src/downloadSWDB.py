import urllib, zipfile, arcpy, re, os
# downloads the SWDB database from http://dds.cr.usgs.gov/srtm/version2_1/SWBD/ and unzips all of the files
HTTP_ADDRESS = "http://dds.cr.usgs.gov/srtm/version2_1/SWBD/"
for folder in ['SWBDwest', 'SWBDeast']:
    arcpy.AddMessage("Getting file information for " + folder)
    html = urllib.urlopen(HTTP_ADDRESS + folder + "/")
    text = html.read()
    html.close()
    filenames = [s[1:] for s in re.findall("[^ ][ew][0-9]*[ns][0-9]*[afiens].zip", text)]
    arcpy.AddMessage(str(len(filenames)) + " files found for " + folder)
    counter = 1
    for filename in filenames:
        fullfilename = HTTP_ADDRESS + folder + "/" + filename
        arcpy.AddMessage("Downloading " + fullfilename + " (" + str(counter) + "/" + str(len(filenames)) + ")")
        f, h = urllib.urlretrieve(fullfilename)
        zip = zipfile.ZipFile(f)
        zip.extractall("E:/cottaan/My Documents/ArcGIS/SWDB")
        arcpy.AddMessage("Extracting " + os.path.basename(fullfilename) + "\n")
        counter = counter + 1
