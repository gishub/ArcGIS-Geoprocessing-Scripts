import numpy as np
import Image
from scipy.sparse import *
CELLSIZE = 1222.9924525618553 #cell size at zoom 15
OFFSET = 20037508.3428        #offset for the web mercator projection
def numpyToImage(numpyfile, imagefile):
    dt = np.dtype([('quadkey', 'S15'), ('x', np.int16), ('y', np.int16), ('z', np.int16), ('objid', np.int32), ('typeid', np.int16)])
    data = np.loadtxt(numpyfile, delimiter=",", dtype=dt)#load the numpy data (this will be in a single array of quadkey,x,y,z,objid,typeid
    arcpy.AddMessage(data['x'])
    minx = min(data['x']) #get the minx value
    maxx = max(data['x']) #get the maxx value
    miny = min(data['y']) #get the miny value
    maxy = max(data['y']) #get the maxy value
    arcpy.AddMessage("minx:" + str(minx) + " maxx:" + str(maxx) + " miny:" + str(miny) + " maxy:" + str(maxy))
    width = maxx - minx + 1   #get the width of the resulting image
    height = maxy - miny + 1  #get the height of the resulting image
    arcpy.AddMessage("width:" + str(width) + " height:" + str(height))
    data['x'].__isub__(minx) #change the x values to be zero based by subtracting the minx value
    data['y'].__imul__(-1)   #do the same with the y values using a different calculation
    data['y'].__iadd__(maxy)
    arcpy.AddMessage(data['x'])
    arcpy.AddMessage(data['y'])
    arcpy.AddMessage(data['z'])
    pixels = coo_matrix((data['z'], (data['y'], data['x'])), shape=(height, width)).todense() #convert the sparse array into a dense matrix, i.e. by adding in all of the zero values
    arcpy.AddMessage(pixels)
    image = Image.fromarray(pixels) #create the output tif from the pixel values
    image.save(imagefile) #save the image to a file
    f = open(imagefile[:-3] + "tfw", 'w') #open the tfw file to write the georeferencing coordinates in
    f.write(str(CELLSIZE) + "\n0.0000000000\n0.0000000000\n-" + str(CELLSIZE) + "\n") #you need to set the y cell size as a minus number otherwise the image is upside down
    topleftx = (minx * CELLSIZE) - OFFSET + (CELLSIZE / 2) #get the top left x coordinate
    toplefty = (maxy * CELLSIZE) - OFFSET + (CELLSIZE / 2) #get the top left y coordinate
    f.write(str(topleftx) + "\n")  #top left x coordinate
    f.write(str(toplefty) + "\n")  #top left y coordinate
    f.close() #close the file
    
numpyfile = arcpy.GetParameterAsText(0)
imagefile = arcpy.GetParameterAsText(1)
numpyToImage(numpyfile, imagefile) #convert the numpy file to an image
