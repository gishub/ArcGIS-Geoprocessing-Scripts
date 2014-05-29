import fao_utilities, netCDF4, os, numpy
from netCDF4 import Dataset
param = {"name":"prodx", "longname":"production for crop group", "unit":"hg/pixel", "expression":"crop area x yield x *100000 for all crops"}
groups = fao_utilities.GetCropGroupsAndFilenames(param['name'])
for i in range(1, 12):
    items = [group[1] for group in groups if group[0] == str(i)]  # get the search string of the files to match, e.g. ['_carea_sea_trri_ir', '_carea_sea_trri_rf']
    files = fao_utilities.GetFilesForGroup(items)  # get the gz files to process for this group
    for climateModel in ["_can_", "_gfd_", "_mir_"]:  # filter for the files containing only the climate model
        for scenario in ["_B1_", "_B2_"]:  # filter for the files containing only the scenario model
            filteredFiles = [f for f in files if climateModel in f[1] and scenario in f[1]]  # get the files to process
            if len(filteredFiles) > 0:
                print "Processing group: " + str(i) + " climate model: " + climateModel + " scenario: " + scenario
                f = filteredFiles[0][0]
                outputNetCDF = fao_utilities.OUTPUT_DATA + os.path.basename(f)[:os.path.basename(f).find(param["name"] + "_sea_") + 10] + "gr" + str(i).zfill(2) + ".nc"  # get the path for the new netcdf file
                outputNetCDFZip = fao_utilities.GetNetCDFZipOutputFilename(outputNetCDF)
                if outputNetCDFZip:
                    total = None
                    for j in range(len(filteredFiles)):
                        file = filteredFiles[j]
                        inputNetCDF = fao_utilities.UnzipGZFile(file[0], file[1])  # unzip the gz file
                        dataset = Dataset(inputNetCDF)  # load into memory
                        data = dataset.variables[param["name"]][:]
                        if total==None:  # add the data to the total
                            total = data
                        else:
                            total = total.__add__(data) 
                        if j==len(filteredFiles)-1:
                            fao_utilities.CreateNetCDFFile(dataset, total, outputNetCDF, param['name'], param['longname'], param['unit'], file[0], param['expression'], "Year 2000")  # create the netcdf file
                        dataset.close()
                        os.remove(inputNetCDF)
                else:
                    print "Output already exists - skipping"
