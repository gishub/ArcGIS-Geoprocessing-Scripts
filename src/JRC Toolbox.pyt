import avro, json
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, SchemaResolutionException
from datetime import date
import arcpy, numpy
# constants
FEATURE_CLASS_LAYER = "fc_layer"
FEATURE_GROUPS_FREQUENCY = "feature_groups_frequency"
SPACER = "    "
groupIDs = [0]

def addNewGroupID():
    newgroupid = len(groupIDs)
    groupIDs.append(newgroupid)
    return newgroupid
        
def getGroupID(groups_for_overlapping_features):
    if len(set(groupIDs) - set(groups_for_overlapping_features)) == 0:
        return addNewGroupID()
    else:
        valid_group_ids = list((set(groupIDs) - set(groups_for_overlapping_features)))
        group_id = valid_group_ids[len(valid_group_ids) - 1] 
        if group_id == 0:
            group_id = addNewGroupID()
        return group_id

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "JRC Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [TabulateAreaForFeatureDataset, ExplodeOverlappingPolygons, FeatureClassToAvro]


class TabulateAreaForFeatureDataset(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "TabulateArea for FeatureDataset"
        self.description = "Iterates through all feature classes in a feature dataset and computes the zonal statistics for each feature class and appends the results into a single output table"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Feature dataset", name="in_feature_dataset", datatype="DEFeatureDataset", parameterType="Required", direction="Input")
        param1 = arcpy.Parameter(displayName="Zone field", name="in_zone_field", datatype="GPString", parameterType="Required", direction="Input")
        param1.value = "wdpaid"
        param2 = arcpy.Parameter(displayName="Raster dataset", name="in_raster_dataset", datatype="GPRasterLayer", parameterType="Required", direction="Input")
        param3 = arcpy.Parameter(displayName="Class field", name="in_class_field", datatype="Field", parameterType="Required", direction="Input")
        param3.value = "Value"
        param4 = arcpy.Parameter(displayName="Output table name", name="out_table_name", datatype="GPString", parameterType="Required", direction="Input")
        param4.value = "tabulate_area"
        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
#         if parameters[0].value:  # if the feature dataset has been set - get the first feature classes fields
#             arcpy.env.workspace = parameters[0].valueAsText
#             featureclasses = arcpy.ListFeatureClasses()
#             if len(featureclasses) > 0:
#                 desc = arcpy.Describe(featureclasses[0])
#                 parameters[1].value = desc.fields[0]
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        try:
            """The source code of the tool."""
            feature_dataset = parameters[0].valueAsText  # get the featuredataset
            zone_field = parameters[1].valueAsText  # get the zone_field
            input_raster = parameters[2].valueAsText  # get the input raster
            arcpy_raster = arcpy.Raster(input_raster)
            raster_layer = arcpy.MakeRasterLayer_management(input_raster)  # create a raster layer to get the attribute table
            if arcpy_raster.hasRAT:
                arcpy.AddMessage("Raster attribute table found")
            else:
                arcpy.AddMessage("No raster attribute table found - creating one")
                # TODO create the raster attribute table
            class_field = parameters[3].valueAsText  # get the class_field
            output_table_name = parameters[4].valueAsText  # get the output table name
            desc = desc = arcpy.Describe(feature_dataset)
            filegdbpath = desc.path
            arcpy.env.workspace = feature_dataset
            featureclasses = arcpy.ListFeatureClasses()
            arcpy.env.workspace = filegdbpath
            arcpy.env.extent = "MINOF"
            arcpy.env.snapRaster = input_raster
            if arcpy.Exists(output_table_name):
                arcpy.AddMessage("Output table " + output_table_name + " already exists")
            else:
                # create the output table - first get the unique values in the raster
                raster_attribute_table = arcpy.SearchCursor(raster_layer)  # get the attribute table
                value_list = []
                for row in raster_attribute_table:  # iterate through the unique values and build up a list of fields
                     value_list.append(row.Value)
                arcpy.AddMessage("Creating the output table")
                arcpy.CreateTable_management(arcpy.env.workspace, output_table_name, "#", "#")
                arcpy.AddField_management(output_table_name, zone_field, "LONG", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
                arcpy.AddField_management(output_table_name, "VALUE", "LONG", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
                for value in value_list:
                    arcpy.AddMessage("Adding field " + "VALUE_" + str(value))
                    arcpy.AddField_management(output_table_name, "VALUE_" + str(value), "DOUBLE", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")
            # iterate through the feature classes
            for featureclass in featureclasses:  
                arcpy.AddMessage("Converting " + featureclass + " to raster")
                arcpy.PolygonToRaster_conversion(featureclass, zone_field, "tmp_raster", "MAXIMUM_AREA", zone_field, "0.0089285714")
                arcpy.AddMessage("Updating the raster attribute table for  " + featureclass)
                arcpy.BuildRasterAttributeTable_management("tmp_raster", "Overwrite")
                arcpy.AddMessage("TabulateArea for " + featureclass)
                arcpy.gp.TabulateArea_sa("tmp_raster", "Value", raster_layer, "Value", "tmp_statistics", "0.0089285714")
                arcpy.AddMessage("Appending results")
                arcpy.Append_management("tmp_statistics", output_table_name, "NO_TEST")
                arcpy.Delete_management("tmp_raster")
                arcpy.Delete_management("tmp_statistics")
            arcpy.AddMessage("Creating the final output table")
            output_table_view = arcpy.MakeTableView_management(output_table_name)
            arcpy.AddMessage("Calculating the unique key")
            arcpy.CalculateField_management(output_table_view, zone_field, "[VALUE]", "VB", "#")
            arcpy.AddMessage("Deleting temporary tables")
            arcpy.DeleteField_management(output_table_name, "VALUE")
            arcpy.Delete_management(output_table_view)
            arcpy.Delete_management(raster_layer)
        except:
             arcpy.AddMessage("Something really bad happened")
        return

class ExplodeOverlappingPolygons(object):
    # this is based on the graph colouring method found here: http://gis.stackexchange.com/questions/32217/exploding-overlapping-to-new-non-overlapping-polygons
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Explode overlapping polygons"
        self.description = "Creates a new set of feature classes from a feature class that remove all overlapping polygons."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input feature class",
            name="input_feature_class",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        return [param0]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        fc = parameters[0].valueAsText
        desc = arcpy.Describe(fc)
        featuredataset = desc.path[desc.path.rfind("\\") + 1:]
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = r"E:\cottaan\My Documents\ArcGIS\PA GLC2000 Analysis\default.gdb"
        # buffer the polygons
        buffer = True
        if buffer:
            arcpy.AddMessage("STEP 1: Buffering input features")
            arcpy.AddMessage(SPACER + "Adding the unbuffered_fc_OBJECTID field")
            arcpy.AddField_management(fc, "unbuffered_fc_OBJECTID", "LONG", "#", "#", "#", "#", "NULLABLE", "NON_REQUIRED", "#")  # when you buffer a fc the features are not preserved in the same order so we need to make sure we can get the original OBJECTIDs at the end
            arcpy.AddMessage(SPACER + "Populating the unbuffered_fc_OBJECTID field")
            arcpy.CalculateField_management(fc, "unbuffered_fc_OBJECTID", "!OBJECTID!", "PYTHON_9.3", "#")
            arcpy.AddMessage(SPACER + "Buffering")
            arcpy.Buffer_analysis(fc, featuredataset + "/fc_buffer", "0.01 DecimalDegrees", "FULL", "ROUND", "NONE", "#")
            arcpy.AddMessage(SPACER + "Removing the unbuffered_fc_OBJECTID field")
            arcpy.DeleteField_management(fc, "unbuffered_fc_OBJECTID")  
            topologyFeatureClass = featuredataset + "/fc_buffer"
        else:
            topologyFeatureClass = fc
        # get the overlaps from the topology
        arcpy.AddMessage("STEP 2: Getting overlapping features")
        arcpy.AddMessage(SPACER + "Creating topology")
        arcpy.CreateTopology_management(featuredataset, "topo1")
        arcpy.AddMessage(SPACER + "Adding feature class to topology")
        arcpy.AddFeatureClassToTopology_management(featuredataset + "/topo1", topologyFeatureClass, "1", "1")
        arcpy.AddMessage(SPACER + "Adding topology rule")
        arcpy.AddRuleToTopology_management(featuredataset + "/topo1", "Must Not Overlap (Area)", topologyFeatureClass, "#", "#", "#")
        arcpy.AddMessage(SPACER + "Validating topology")
        arcpy.ValidateTopology_management(featuredataset + '/topo1')
        arcpy.AddMessage(SPACER + "Exporting topology errors")
        arcpy.ExportTopologyErrors_management(featuredataset + "/topo1", featuredataset, "topoerrors")  # errors will be in topoerrors_poly
        arcpy.AddMessage(SPACER + "Getting unique overlapping polygons")
        arcpy.Frequency_analysis(featuredataset + "/topoerrors_poly", "topoerrors_poly_Frequency", "OriginObjectID;DestinationObjectID", "#")  # get the unique overlapping features
        arcpy.CopyRows_management("topoerrors_poly_Frequency", "topoerrors_poly_Frequency2", "#")  # copy the table so we can append the inverse overlapping features
        arcpy.Append_management("topoerrors_poly_Frequency2", "topoerrors_poly_Frequency", "NO_TEST", """FREQUENCY "FREQUENCY" true true false 4 Long 0 0 ,First,#,topoerrors_poly_Frequency2,FREQUENCY,-1,-1;OriginObjectID "Feature 1" true true false 4 Long 0 0 ,First,#,topoerrors_poly_Frequency2,DestinationObjectID,-1,-1;DestinationObjectID "Feature 2" true true false 4 Long 0 0 ,First,#,topoerrors_poly_Frequency2,OriginObjectID,-1,-1""", "#")  # append the inverse overlapping features
        arcpy.Delete_management(r'topoerrors_poly_Frequency2')  # delete the temporary table
        arcpy.AddMessage(SPACER + "Getting the count of overlapping polygons")
        arcpy.Frequency_analysis("topoerrors_poly_Frequency", "unique_overlaps", "OriginObjectID", "#")  # create the unique overlaps table which will have the FREQUENCY, feature1 OBJECTID
        arcpy.Sort_management("unique_overlaps", "unique_OriginObjectIDs", "FREQUENCY DESCENDING", "UR")
        arcpy.AddMessage(SPACER + "Adding an overlap count field to the unique overlaps")
        arcpy.AddField_management("topoerrors_poly_Frequency", "overlap_count", "SHORT", "#", "#", "255", "#", "NULLABLE", "NON_REQUIRED", "#")
        arcpy.AddMessage(SPACER + "Adding a group field to compute the disjoint collection of features")
        arcpy.AddField_management("topoerrors_poly_Frequency", "grp", "LONG", "#", "#", "255", "#", "NULLABLE", "NON_REQUIRED", "#")
        arcpy.AddMessage(SPACER + "Adding indexes to speed up the joins")
        arcpy.AddIndex_management("topoerrors_poly_Frequency", "OriginObjectID;DestinationObjectID", "index1", "NON_UNIQUE", "NON_ASCENDING")
        arcpy.AddMessage(SPACER + "Joining unique overlapping polygon table to frequency table")
        arcpy.MakeTableView_management(r'topoerrors_poly_Frequency', "topoerrors_poly_Frequency_tv")  # make a table view of the table
        arcpy.MakeTableView_management(r'unique_overlaps', "unique_overlaps_tv")  # make a table view of the table
        arcpy.AddJoin_management("topoerrors_poly_Frequency_tv", "OriginObjectID", "unique_overlaps_tv", "OriginObjectID", "KEEP_ALL")
        arcpy.AddMessage(SPACER + "Populating the overlap count field")
        arcpy.CalculateField_management("topoerrors_poly_Frequency_tv", "overlap_count", "[unique_overlaps.FREQUENCY]", "VB", "#")
        arcpy.AddMessage(SPACER + "Removing join")
        arcpy.RemoveJoin_management("topoerrors_poly_Frequency_tv", "unique_overlaps")
        arcpy.AddMessage(SPACER + "Sorting data to compute groups")
        arcpy.Delete_management("topoerrors_poly_Frequency_tv")
        arcpy.Delete_management("unique_overlaps_tv")
        arcpy.Sort_management("topoerrors_poly_Frequency", "unique_overlaps_sorted", "overlap_count DESCENDING", "UR")
        arcpy.AddMessage(SPACER + "Deleting the temporary tables")
        arcpy.Delete_management(r'unique_overlaps')  # delete the temporary table
        arcpy.Delete_management(r'topoerrors_poly_Frequency')  # delete the temporary table
        arcpy.AddMessage(SPACER + "Deleting the topologies")
        arcpy.Delete_management(featuredataset + '/topo1')  # delete the topology
        arcpy.Delete_management(featuredataset + '/topoerrors_line')  # delete the line topo errors
        arcpy.Delete_management(featuredataset + '/topoerrors_point')  # delete the point topo errors
        arcpy.Delete_management(featuredataset + '/topoerrors_poly')  # delete the poly topo errors
        # create the non-overlapping feature groups
        arcpy.AddMessage("STEP 3: Creating the groups of non-overlapping features")
        arcpy.AddMessage(SPACER + "Iterating through the features to create the groups")
        unique_origin_ids = [int(t[0]) for t in arcpy.da.TableToNumPyArray("unique_OriginObjectIDs", "OriginObjectID").tolist()]
        feature_groups = arcpy.da.TableToNumPyArray("unique_overlaps_sorted", ["OriginObjectID", "DestinationObjectID", "overlap_count", "grp"], null_value=0)
        for unique_origin_id in unique_origin_ids:
        #     arcpy.AddMessage(SPACER + SPACER + "Feature: " + str(unique_origin_id))
            overlapping_feature_ids = feature_groups[numpy.where(feature_groups['OriginObjectID'] == unique_origin_id)]['DestinationObjectID']
        #     arcpy.AddMessage(SPACER + SPACER + "Overlapping features: " + ",".join([str(id) for id in overlapping_feature_ids]))
            groups_for_overlapping_features = list(set(feature_groups[numpy.in1d(feature_groups['OriginObjectID'], overlapping_feature_ids)]['grp']))
        #     arcpy.AddMessage(SPACER + SPACER + "Overlapping feature groups: " + ",".join([str(id) for id in groups_for_overlapping_features]))
            groupID = getGroupID(groups_for_overlapping_features)
        #     arcpy.AddMessage(SPACER + SPACER + "Assigning group " + str(groupID) + " to feature " + str(unique_origin_id))
            for i in numpy.where(feature_groups['OriginObjectID'] == unique_origin_id)[0]:
                feature_groups[i]['grp'] = groupID
        arcpy.AddMessage(SPACER + "Deleting the temporary tables")
        arcpy.Delete_management('unique_OriginObjectIDs')  # delete the unique_OriginObjectIDs table
        arcpy.Delete_management('unique_overlaps_sorted')  # delete the unique_overlaps_sorted table
        arcpy.AddMessage(SPACER + "Creating final output table of non-overlapping feature groups")        
        table_name = arcpy.env.workspace + "/feature_groups"
        arcpy.da.NumPyArrayToTable(feature_groups, table_name)
        arcpy.AddMessage(SPACER + "Getting the unique feature groups")
        arcpy.Frequency_analysis("feature_groups", "feature_groups_Frequency1", "OriginObjectID;grp", "#")
        arcpy.Delete_management("feature_groups")
        arcpy.AddMessage(SPACER + "Adding the grp field to the feature class")
        if buffer:
            arcpy.AddMessage(SPACER + "Recreating original OBJECTID values")
            arcpy.AddField_management('feature_groups_Frequency1', 'unbuffered_fc_OBJECTID', "LONG")
            tv = arcpy.MakeTableView_management('feature_groups_Frequency1')
            fl = arcpy.MakeFeatureLayer_management(featuredataset + '/fc_buffer')
            arcpy.AddJoin_management(tv, "OriginObjectID", fl, "OBJECTID")
            arcpy.CalculateField_management(tv, "feature_groups_Frequency1.unbuffered_fc_OBJECTID", "[fc_buffer.unbuffered_fc_OBJECTID]", "VB", "#")
            arcpy.RemoveJoin_management(tv, "fc_buffer")
            arcpy.CalculateField_management(tv, "OriginObjectID", "[unbuffered_fc_OBJECTID]", "VB", "#")
            arcpy.DeleteField_management(tv, "unbuffered_fc_OBJECTID")
            arcpy.Delete_management(featuredataset + '/fc_buffer')  # delete the buffered features
            arcpy.Delete_management(tv)
            arcpy.Delete_management(fl)
        arcpy.JoinField_management(fc, "OBJECTID", "feature_groups_Frequency1", "OriginObjectID", "grp")
        arcpy.Delete_management("feature_groups_Frequency1")
#         arcpy.AddMessage(SPACER + "Creating group 0 for non-overlapping features")
        arcpy.MakeFeatureLayer_management(fc, FEATURE_CLASS_LAYER)
        arcpy.SelectLayerByAttribute_management(FEATURE_CLASS_LAYER, "NEW_SELECTION", "grp IS Null")
        count = arcpy.GetCount_management(FEATURE_CLASS_LAYER)
#         arcpy.AddMessage(SPACER + str(count) + " records selected")
        arcpy.CalculateField_management(FEATURE_CLASS_LAYER, "grp", "0", "VB", "#")
        arcpy.SelectLayerByAttribute_management(FEATURE_CLASS_LAYER, "CLEAR_SELECTION")
        arcpy.AddMessage(SPACER + "Getting the unique non-overlapping feature groups to export")
        arcpy.Frequency_analysis(FEATURE_CLASS_LAYER, FEATURE_GROUPS_FREQUENCY, "grp", "#")
        unique_non_overlapping_groups = arcpy.da.TableToNumPyArray(FEATURE_GROUPS_FREQUENCY, "grp").tolist()
        arcpy.Delete_management(FEATURE_GROUPS_FREQUENCY)
        # Exporting the groups of non-overlapping features
        arcpy.AddMessage("STEP 4: Exporting the groups of non-overlapping features")
        arcpy.AddMessage(SPACER + "Creating the feature dataset")
        arcpy.CreateFeatureDataset_management(arcpy.env.workspace, desc.name + "_feature_groups", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision")
        for unique_non_overlapping_group in unique_non_overlapping_groups:
            group_id = str(unique_non_overlapping_group[0])
            arcpy.AddMessage(SPACER + SPACER + "Exporting group " + group_id)
            expression = "grp = " + group_id
            arcpy.SelectLayerByAttribute_management(FEATURE_CLASS_LAYER, "NEW_SELECTION", expression)
            arcpy.FeatureClassToFeatureClass_conversion(FEATURE_CLASS_LAYER, desc.name + "_feature_groups", desc.name + "_" + str(group_id).zfill(3))
        arcpy.AddMessage(SPACER + "Deleting the temporary tables and the grp field from the feature class")
        arcpy.Delete_management(FEATURE_CLASS_LAYER)
        arcpy.DeleteField_management(fc, "grp")
        return

class FeatureClassToAvro(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FeatureClass to Avro"
        self.description = "Exports a FeatureClass to an Apache Avro file using deflate compression"
        self.canRunInBackground = False

    def getParameterInfo(self):
        param0 = arcpy.Parameter(displayName="Input feature class", name="input_feature_class", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
        param1 = arcpy.Parameter(displayName="Output folder", name="output_folder", datatype="DEFolder", parameterType="Required", direction="Input")
        param1.value = "E:/export/"
        param2 = arcpy.Parameter(displayName="Use Well-Known Binary", name="use_wkb", datatype="GPBoolean", parameterType="Optional", direction="Input")
        param2.value = True
        return [param0, param1, param2]
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        fc = parameters[0].valueAsText
        outputFolder = parameters[1].valueAsText
        use_wkb = parameters[2].value
        if (use_wkb == True):
            arcpy.AddMessage("Using WKB")
        else:
            arcpy.AddMessage("Using WKT")
        desc = arcpy.Describe(fc)
        outputfilePrefix = outputFolder + "/" + desc.name
        arcpy.AddMessage("Writing Avro file to " + outputfilePrefix + ".avro")
        
        # get the field list for the feature class
        fields = arcpy.ListFields(fc)
        fieldsArray = []
        for field in fields:
            if field.type in ["OID"]:
                fieldType = 'long'
            elif field.type in ["SmallInteger", "Integer"]:
                fieldType = 'int'
            elif field.type == "Geometry":
                if use_wkb:
                    fieldType = 'bytes'
                else:
                    fieldType = 'string'
            elif field.type == "Date":
                fieldType = 'string'
            else:
                fieldType = field.type.lower()
            if field.isNullable:
                fieldsArray.append({"name": field.name, "type": [fieldType, "null"]})
            else:
                fieldsArray.append({"name": field.name, "type": fieldType})
        
        # create the schema from the fields
        schemajson = {"type": "record", "name": desc.name, "fields": fieldsArray }
        schemajsonstr = json.dumps(schemajson, None)
        f = open(outputfilePrefix + ".avsc", "w")
        f.write(schemajsonstr)
        f.close()
        schema = avro.schema.parse(schemajsonstr)
        arcpy.AddMessage("Schema written to " + outputfilePrefix + ".avsc")
        
        # open a writer to write the data
        writer = DataFileWriter(open(outputfilePrefix + ".avro", "wb"), DatumWriter(), schema, "deflate")
         
        # get a cursor to the records
        cursor = arcpy.SearchCursor(fc)
         
        # get the count
        total = str(arcpy.GetCount_management(fc))
         
        # iterate through the records and write the dtaa
        row = cursor.next()
        count = 0
        while row:
            arcpy.AddMessage("Processing " + str(count + 1) + " of " + str(total) + " rows")
            data = {}
            for field in fields:
                if row.getValue(field.name) != None:
                    if field.name.lower() in ["shape", "geom"]:
                        if use_wkb:
                            data[field.name] = bytes(row.getValue(field.name).WKB)
                        else:
                            data[field.name] = row.getValue(field.name).WKT  
                    elif field.type == "Date":
                        data[field.name] = date.isoformat(row.getValue(field.name))
                    else:
                        data[field.name] = row.getValue(field.name)
            writer.append(data)
            row = cursor.next()
            count = count + 1
        #     if count == 50:
        #         break
        writer.close()
        arcpy.AddMessage("Data written to " + outputfilePrefix + ".avro")
#         print "\nChecking file.."
#         arcpy.AddMessage("\nChecking file..")
#         reader = DataFileReader(open(outputfilePrefix + ".avro", "rb"), DatumReader())
#         for record in reader:
#             pass
#         #     print record
#         reader.close()
#         print "Finished" 
#         arcpy.AddMessage("Finished")
