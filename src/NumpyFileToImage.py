import numpy
import Image
from scipy.sparse import *
def numpyToImage(numpyfile,imagefile):
    data=numpy.load(numpyfile)
    data3d=numpy.reshape(data,(3,len(data)/3))
    minx=min(data3d[0])
    maxx=max(data3d[0])
    miny=min(data3d[1])
    maxy=max(data3d[1])
    width=maxx-minx
    height=maxy-miny
    data3d[0].__isub__(minx)
    data3d[1].__imul__(-1)
    data3d[1].__iadd__(maxy)
    pixels=coo_matrix((data3d[2],(data3d[1],data3d[0])), shape=(height+1,width+1)).todense()
    image = Image.fromarray(pixels)
    image.save(imagefile)
    
numpyfile=arcpy.GetParameterAsText(0)
imagefile=arcpy.GetParameterAsText(1)
numpyToImage(numpyfile,imagefile)