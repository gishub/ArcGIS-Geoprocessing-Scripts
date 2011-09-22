import numpy,os,time,cPickle

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

path = arcpy.GetParameterAsText(0) #get the path to the npy files
arcpy.env.workspace = path
quadkeys={} #instantiate an empty dictionary object to hold the quadtrees data
for file in arcpy.ListFiles("*.npy"): #iterate through the npy files
    fileinfo=os.stat(arcpy.env.workspace + os.sep + file)
    speciesID=file[2:-4] #get the species ID
    if fileinfo.st_size>0:
        cells=numpy.load(arcpy.env.workspace + os.sep + file) #load the data
        arcpy.AddMessage("Creating " + str(len(cells)/3) + " records for " + file) 
        coords=numpy.transpose(numpy.reshape(cells,(3,len(cells)/3))) #transpose the data to x,y,z coordinates - z is the status
        for coord in coords: #iterate through each of the coordinates, convert to a quadtree and populate that quadtree file with the species ID
            quadkey= getQuadKey(coord[0],coord[1]) #get the quadtree  
            if (quadkey in quadkeys): #if the quadkey is already in memory
                quadkeys[quadkey]=quadkeys[quadkey] + "\t" + speciesID #append the quadtree to the dictionary item
            else:
                quadkeys[quadkey]=speciesID #create a new dictionary item
        del cells #free memory
        del coords
for quadkey in quadkeys.keys(): #at the end of the processing, write the data to file. One file for each quadtree
    f = open(r"E:\cottaan\My Documents\QuadkeyData" + os.sep + quadkey,'wb')
    cPickle.dump(quadkeys[quadkey], f, protocol=2)
    f.close()