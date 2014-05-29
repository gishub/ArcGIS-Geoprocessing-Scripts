import  os, netCDF4, fao_utilities, numpy
from netCDF4 import Dataset
param = {"name":"carea", "longname":"crop area", "unit":"ha/pixel","expression":"harea*5000","searchStr":"_harea_sea_","replaceStr":"_carea_sea_"}
files = fao_utilities.GetMatchingGZFiles(param["searchStr"])
counter = 1
for file in files:
    gzipfile = file[0]  # get the gz file
    archivename = file[1]  # get the name of the file that will be unzipped
    print "\nProcessing " + os.path.basename(gzipfile) + " (" + str(counter) + "/" + str(len(files)) + ")\n======================================================================================"
    outputNetCDF = fao_utilities.GetNetCDFOutputFilename(archivename, param["searchStr"], param["replaceStr"])  # get the path for the new netcdf file
    outputNetCDFZip = fao_utilities.GetNetCDFZipOutputFilename(outputNetCDF)
    if outputNetCDFZip:
        inputNetCDF = fao_utilities.UnzipGZFile(gzipfile, archivename)  # get the full path of the actual input netcdf file
        try:
            dataset = Dataset(inputNetCDF)  # load the netcdf file into memory
            varname = fao_utilities.GetVariableName(dataset)
            year2000index = numpy.where(dataset.variables['time'][:] == 2000)[0] # get the position of the year 2000 slice
            data = dataset.variables[varname][year2000index, :, :] * 5000  # get the data to write into the new netcdf file
            fao_utilities.CreateNetCDFFile(dataset, data, outputNetCDF, param['name'], param['longname'], param['unit'],file[2], param['expression'], "Year 2000")  # create the netcdf file
            dataset.close()
            os.remove(inputNetCDF)
        except (KeyError)as e:
            print "Key not found: " + str(e) + ". Available keys: " + ",".join([k for k in dataset.variables.keys()])
    else:
        print "Output already exists - skipping"
    counter = counter + 1