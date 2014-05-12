import netCDF4, numpy
from netCDF4 import Dataset
from datetime import date
LATITUDE_DIMENSION_NAME = "lat"
LONGITUDE_DIMENSION_NAME = "lon"
NO_DATA_VALUE = -1
data = Dataset(r"D:/Users/andrewcottam/Documents/ArcGIS/fao/FAO Climate Data/somds.wfdei.cmip5.rcp85.CanESM2.daily.clt.africa.nc")
for key in data.variables:
    if key not in ['lat', 'lon', 'time']:     
        valueDimensionName = key
values = data.variables[valueDimensionName]
indices = []
endyear = date(1960, 1, 1).toordinal() + 
for j in range(1960, 1961):
    for i in range(1, 13):
        index = date(j, i, 1).toordinal() - date(1960, 1, 1).toordinal()
        indices.append({"year":j, "month":i, "startindex":index})
print indices
