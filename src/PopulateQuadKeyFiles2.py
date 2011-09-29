import numpy,os,time,cPickle,arcpy

def getQuadKey(x,y): # returns the quadkey for the passed tile coordinates, e.g. 27025,16973 will return 132320330230021
    quadKey = ""
    y = 32767 -y # the quadkey is based on a y origin based in the northern hemisphere
    for i in range(15, 0, -1):
        digit = 0
        mask = 1 << (i-1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey

def getQuadKeyFilePath(quadkey):
    path="\\"
    for i in range(15):
        path=path + quadkey[i] + os.sep
    folder = r"E:\cottaan\My Documents\QuadkeyData" + path[:31]
    if not (os.path.exists(folder)):
        os.makedirs(folder)
    return folder + "species"
    
path = arcpy.GetParameterAsText(0) #get the path to the npy files
arcpy.env.workspace = path
for file in arcpy.ListFiles("*.npy"): #iterate through the npy files
    fileinfo=os.stat(arcpy.env.workspace + os.sep + file)
    speciesID=file[2:-4] #get the species ID
    if fileinfo.st_size>0:
        cells=numpy.load(arcpy.env.workspace + os.sep + file) #load the data
        arcpy.AddMessage("Creating " + str(len(cells)/3) + " records for " + file) 
        coords=numpy.transpose(numpy.reshape(cells,(3,len(cells)/3))) #transpose the data to x,y,z coordinates - z is the status
        for coord in coords: #iterate through each of the coordinates, convert to a quadtree and populate that quadtree file with the species ID
            quadkey= getQuadKey(coord[0],coord[1]) #get the quadtree
            quadkeyfile=getQuadKeyFilePath(quadkey) # this will save to a hierarchical file structure, e.g. 1\3\2\0\0\0\2\1\3\1\2\0\species
#            quadkeyfile=r"E:\cottaan\My Documents\QuadkeyData" + os.sep + quadkey # this will save all files to the same folder
            if (os.path.exists(quadkeyfile)):
                f = open(quadkeyfile,'ab')
            else:
                f = open(quadkeyfile,'wb')
            cPickle.dump(speciesID, f, protocol=2)
            f.close()                
        del cells #free memory
        del coords