import  os, netCDF4, fao_utilities, numpy, logging
from netCDF4 import Dataset
param = {"name":"prodx", "longname":"production", "unit":"hg/pixel", "expression":"carea*yield*100000", "searchStr1":"_carea_sea_", "searchStr2":"_yield_sea_", "replaceStr":"_prodx_sea_"}
logging.basicConfig(filename=r"D:\Users\andrewcottam\Documents\ArcGIS\fao\processing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
files = fao_utilities.GetMatchingGZFiles(param["searchStr1"])
counter = 1
for file in files:
    gzipfile1 = file[0]  # get the gz file
    gzipfile2 = gzipfile1.replace(param["searchStr1"], "_yield_sea_")
    archivename1 = file[1]  # get the name of the file that will be unzipped
    print "\nProcessing " + os.path.basename(gzipfile1) + " (" + str(counter) + "/" + str(len(files)) + ")\n======================================================================================"
    outputNetCDF = fao_utilities.GetNetCDFOutputFilename(archivename1, param["searchStr1"], param["replaceStr"])  # get the path for the new netcdf file
    outputNetCDFZip = fao_utilities.GetNetCDFZipOutputFilename(outputNetCDF)
    if outputNetCDFZip:
        inputNetCDF1 = fao_utilities.UnzipGZFile(gzipfile1, archivename1)  # get the full path of the actual input netcdf file
        archivename2 = fao_utilities.GetCorrespondingFile(archivename1, param['searchStr1'], param['searchStr2'])
        inputNetCDF2 = fao_utilities.UnzipGZFile(gzipfile2, archivename2)  # get the full path of the actual input netcdf file
        try:
            dataset1 = Dataset(inputNetCDF1)  # load the first input netcdf file into memory
            dataset2 = Dataset(inputNetCDF2)  # load the second input netcdf file into memory
            varname1 = fao_utilities.GetVariableName(dataset1) # get the variable name of the first dataset
            varname2 = fao_utilities.GetVariableName(dataset2) # get the variable name of the second dataset
            data1 = dataset1.variables[varname1][:, :, :]  # get the data from the first dataset
            year2000index = numpy.where(dataset2.variables['time'][:] == 2000)[0]  # get the position of the year 2000 slice in the second netcdf file
            data2 = fao_utilities.GetNetCDFData(dataset2, varname2)[year2000index, :, :] # get the data from the second dataset
            data = data1 * data2 * 100000 # do the calculation
            fao_utilities.CreateNetCDFFile(dataset1, data, outputNetCDF, param['name'], param['longname'], param['unit'], inputNetCDF1 + " and " + inputNetCDF2, param['expression'], "Year 2000")  # create the netcdf file
            dataset1.close()
            dataset2.close()
            os.remove(inputNetCDF1)
            os.remove(inputNetCDF2)
        except (KeyError)as e:
            print "Key not found: " + str(e) + ". Available keys: " + ",".join([k for k in dataset1.variables.keys()]) + " and " + ",".join([k for k in dataset2.variables.keys()])
        except (MemoryError)as e:
            logging.error("MemoryError while creating " + os.path.basename(outputNetCDFZip))
            print "MemoryError while creating " + os.path.basename(outputNetCDFZip)
        except (WindowsError)as e:
            print e
    else:
        print "Output already exists - skipping"
    counter = counter + 1