import arcpy
in_netcdf = "D:/Users/andrewcottam/Documents/ArcGIS/fao/FAO Climate Data/somds.wfdei.cmip5.rcp85.CanESM2.daily.clt.africa.nc"
try:
    nc_fp = arcpy.NetCDFFileProperties(in_netcdf)

    # Get Variables
    for nc_var in nc_fp.getVariables():
        print("Variable: {0}".format(nc_var))
        print("\tVariable type: {0}".format(nc_fp.getFieldType(nc_var)))

        # Get dimensions by variable
        for nc_dim_by_var in nc_fp.getDimensionsByVariable(nc_var):
            print("Dimension: {0}".format(nc_dim_by_var))
        print(nc_fp.getAttributeValue(nc_var, "units"))

        # Get Variable Attribues
        for nc_va_name in nc_fp.getAttributeNames(nc_var):
            print("Attribute Name: {0}".format(nc_va_name))

    # Get Dimensions
    for nc_dim in nc_fp.getDimensions():
        print("Dimension: {0}".format(nc_dim))
        print("\tDimension size: {0}".format(nc_fp.getDimensionSize(nc_dim)))
        print("\tDimension type: {0}".format(nc_fp.getFieldType(nc_dim)))

        for i in range(0, nc_fp.getDimensionSize(nc_dim)):
            nc_dim_value = nc_fp.getDimensionValue(nc_dim, i)
            print("\tDimension value: {0}".format(nc_dim_value))
            print("\tDimension index: {0}".format(
                nc_fp.getDimensionIndex(nc_dim, nc_dim_value)))

        # Get Variable by dimension
        for nc_vars_by_dim in nc_fp.getVariablesByDimension(nc_dim):
            print("\tVariable by dimension: {0}".format(nc_vars_by_dim))

    # Get Global Attribues
    for nc_att_name in nc_fp.getAttributeNames(""):
        print("Attribute Name: {0}".format(nc_att_name))
        print(nc_fp.getAttributeValue("", nc_att_name))

except Exception as err:
    print(err)