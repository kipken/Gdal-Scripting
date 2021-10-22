from osgeo import gdal
import numpy as np
import subprocess
import pandas as pd
import csv
import json

'''
    a function that creates a new RAT by joining input csv//
    with default rat,
    NB: convert your data to a csv before implementing the func
    
'''


def create_new_raster(input_raster_name, output_file_name):
    '''
    :param input_raster_name: this is the filename of the raster, it should have a raster attribute table
    :param output_file_name: the output path to store the created raster
    :return: returns a new raster
    '''
    driver = gdal.GetDriverByName('GTiff')
    input_raster = gdal.Open(input_raster_name)
    my_array = np.array(input_raster.GetRasterBand(1).ReadAsArray())
    print(my_array)
    values, count = np.unique(my_array, return_counts=True)
    # print(list(values))
    # create raster
    output_raster = driver.Create(output_file_name, input_raster.RasterXSize,
                                  input_raster.RasterYSize, 1)
    output_raster.GetRasterBand(1).WriteArray(my_array)
    proj = input_raster.GetProjection()
    geo_ref = input_raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    return output_raster


# if a raster has an existing RAT and you want to perform a join//
# call this function
# before running this ensure the RAT of the input image is activated
def join_csv_with_rat(input_raster, output_file_name, input_csv):
    '''
    :param input_raster: this is the raster name to be used for join
    :param output_file_name: the output raster file path
    :param input_csv: the csv with which to use for joining
    :return: None
    '''
    # create a new raster
    out_put_path = "new_raster_csv.tif"
    new_ras = create_new_raster(input_raster, output_file_name)
    print("Opening the image in update mode....")
    input_ras = gdal.Open(input_raster, gdal.GA_Update)
    input_band = input_ras.GetRasterBand(1)
    input_rat = input_band.GetDefaultRAT()
    # read csv as dataframe
    df = pd.read_csv(input_csv)
    # get length of cols and rows
    rat_col_len = input_rat.GetColumnCount()
    rat_row_len = input_rat.GetRowCount()
    # get column names both csv and rat
    rat_col_names = []
    for i in range(rat_col_len):
        rat_col_names.append(input_rat.GetNameOfCol(i))
    csv_col_names = list(df.columns)
    # all column names both rat and csv
    combined_col_names = list(np.hstack([rat_col_names, csv_col_names]))
    # get colytypes from both csv and RAT
    rat_col_types = []
    for i in range(rat_col_len):
        if input_rat.GetTypeOfCol(i) == gdal.GFT_String:
            rat_col_types.append("string")
        elif input_rat.GetTypeOfCol(i) == gdal.GFT_Real:
            rat_col_types.append("double")
        elif input_rat.GetTypeOfCol(i) == gdal.GFT_Integer:
            rat_col_types.append("integer")

    csv_col_types = []

    for i in range(len(csv_col_names)):
        if df.iloc[:, i].dtype == "object":
            csv_col_types.append("string")
        elif df.iloc[:, i].dtype == "int64":
            csv_col_types.append("integer")
        elif df.iloc[:, i].dtype == "float64" or "float32":
            csv_col_types.append("double")
        else:
            csv_col_types.append("Null")
    # changing from nd array to 1d array
    combined_col_types = list(np.hstack([rat_col_types, csv_col_types]))
    # create a new RAT with column names/fields from csv and RAT
    print("Creating an empty RAT & appending data")
    output_rat = gdal.RasterAttributeTable()
    for c_ix, col_name in enumerate(combined_col_names):
        if combined_col_types[c_ix] == "integer":
            output_rat.CreateColumn(col_name, gdal.GFT_Integer, gdal.GFU_Generic)
        elif combined_col_types[c_ix] == "double":
            output_rat.CreateColumn(col_name, gdal.GFT_Real, gdal.GFU_Generic)
        else:
            output_rat.CreateColumn(col_name, gdal.GFT_String, gdal.GFU_Generic)
    # populating the raster attribute table

    # create a rat list
    rat_list = []
    for idx, vl in enumerate(rat_col_types):
        field_name = rat_col_names[idx]
        val_list = []
        for row in range(rat_row_len):
            if rat_col_types[idx] == "integer":
                # col_val = [rat.GetValueAsInt(row, idx)]
                field_name = rat_col_names[idx]
                # print(new_val)
                val_list.append(input_rat.GetValueAsInt(row, idx))
            elif rat_col_types[idx] == "double":
                field_name = rat_col_names[idx]
                # col_val =[rat.GetValueAsDouble(row,idx)]
                # print(input_rat.GetValueAsDouble(row, idx))
                val_list.append(input_rat.GetValueAsDouble(row, idx))
            elif rat_col_types[idx] == "string":
                field_name = rat_col_names[idx]
                # col_val =[rat.GetValueAsString(row,idx)]
                val_list.append(input_rat.GetValueAsString(row, idx))
        rat_list.append(val_list)
    print("RAT List: {}".format(rat_list))

    # get list from csv
    csv_list = [list(df[i]) for i in csv_col_names]
    print("CSV columns list: {}".format(csv_list))
    combined_col_list = [rat_list, csv_list]
    print("Nth D array of columns")
    print(combined_col_types)
    # populating rat
    col_type_ind = 0
    for l in range(len(combined_col_list)):
        # gets specific lists of rat and csv lists
        for j in range(len(combined_col_list[l])):
            # focuses on specific columns of either rat or csv
            for k in range(len(combined_col_list[l][j])):
                # individual values from columns of specific list
                # print(combined_col_list[l][j][k])
                # [i for i in enumerate(combined_col_types)]
                if combined_col_types[col_type_ind] == "integer":
                    output_rat.SetValueAsInt(k, col_type_ind, combined_col_list[l][j][k])
                elif combined_col_types[col_type_ind] == "double":
                    output_rat.SetValueAsDouble(k, col_type_ind, combined_col_list[l][j][k])
                else:
                    output_rat.SetValueAsString(k, col_type_ind, combined_col_list[l][j][k])
            # print(col_type_ind)
            col_type_ind += 1
    print("get number of column types")
    print(combined_col_list[1][1])
    band = new_ras.GetRasterBand(1)

    band.SetDefaultRAT(output_rat)
    band.FlushCache()
    del new_ras, band,input_ras,input_band
    # get values from RAT
    # create a rat_list with both values of csv and RAT
    # populate the created RAT
    # set default rat for new raster to created RAT


def attribute_csv_join(input_csv, raster_filename,out_put_file, join_field):
    attraction_raster = raster_filename

    '''
        This code reads a raster, gets unique values 
    '''
    attraction_ds = gdal.Open(attraction_raster,
                              gdal.GA_Update | gdal.OF_UPDATE)  # open in update mode with gdal.GA_Update
    '''
        check for existence of RAT
    '''
    check_band = attraction_ds.GetRasterBand(1)
    check_rat = check_band.GetDefaultRAT()
    if check_rat is None:
        my_array = np.array(attraction_ds.GetRasterBand(1).ReadAsArray())
        values, count = np.unique(my_array, return_counts=True)
        print(type(values))
        # print(attraction_ds.values())
        df = pd.DataFrame({'unique_value': values, 'COUNT': count})

        print("{}:{}".format(values, count))

        '''
            the code below:
            1. creates an empty raster attribute table
            2. Populates it with values.
            3. stores the attribute info to the raster
            
            
        '''
        # create an empty Raster Attribute Table and populate it using the values, their frequency and their class

        attraction_vec = input_csv
        print("Reading raster and csv files....")
        ras_ds = gdal.Open(attraction_raster)
        vec_ds = gdal.Open(attraction_vec)
        n_df = pd.read_csv(attraction_vec)
        print(n_df)
        # lyr = vec_ds.GetLayer()
        geot = ras_ds.GetGeoTransform()
        # get fields
        print("Extracting the csv fields/ column names")

        csv_fields = list(n_df.columns)
        values = list(values)
        unique_field = list(n_df[join_field])
        print("{}:{}".format(unique_field, values))
        # if unique_field not in values:
        #     print('{} not in unique values of raster,check values in your unique csv field'.format(unique_field))
        # else:
        #     print("Values and csv fields are similar, proceed!")
        print("Mapping raster values with user unique field...")
        row_idx_to_use = []
        filtered_fields_row = []
        for idx, val in enumerate(values):
            # print(val)
            for ix, v in enumerate(unique_field):
                if v == val:
                    row_idx_to_use.append(ix)
                    filtered_fields_row.append(ix)
        print("refactor your dataframe for mapping purposes")

        print("{}:{}".format(row_idx_to_use, filtered_fields_row))
        get_data_types = []
        # print(unique_field)
        # get data type for csv
        print("Getting datatypes for each column....")
        for i in range(len(csv_fields)):
            if n_df.iloc[:, i].dtype == "object":
                get_data_types.append("string")
            elif n_df.iloc[:, i].dtype == "int64":
                get_data_types.append("int")
            elif n_df.iloc[:, i].dtype == "float64" or "float32":
                get_data_types.append("float")
            else:
                get_data_types.append("Null")
        print(get_data_types)
        print(len(csv_fields))
        print("Converting csv fields to an array..")
        for n, m in enumerate(csv_fields):
            print(np.asarray(list(n_df[m])))
        # print(len(n_df["class"]))

        '''dynamic updating of raster attribute table'''

        # instantiate an empty raster
        print("Instantiating an empty raster attribute table with columns")
        rat = gdal.RasterAttributeTable()
        # rat.CreateColumn('unique_value', gdal.GFT_Integer, gdal.GFU_Generic)
        # rat.CreateColumn('COUNT', gdal.GFT_Integer, gdal.GFU_Generic)
        '''
            create your columns, column type created based on csv field//
            data type
        '''
        for idx, i in enumerate(csv_fields):
            print(i)
            if get_data_types[idx] == "int":
                rat.CreateColumn(i, gdal.GFT_Integer, gdal.GFU_Generic)
            elif get_data_types[idx] == "float":
                rat.CreateColumn(i, gdal.GFT_Real, gdal.GFU_Generic)
            else:
                rat.CreateColumn(i, gdal.GFT_String, gdal.GFU_Generic)
        print("RAT instantiated")

        print(type(rat))

        #  populating the raster
        print("Populating raster attribute table")
        for ind, row_val in enumerate(row_idx_to_use):
            for x, val in enumerate(csv_fields):
                print(val)
                print(i)
                if get_data_types[x] == "int":
                    print("getting column name")
                    store_val = list(n_df[val])
                    # print(store_val)
                    store = [i for i in store_val]
                    store = np.asarray(store)
                    # print("store val: {}".format(store))
                    len_rows = len(n_df[val])
                    rat.SetValueAsInt(ind, x, int(store[row_val]))
                    # print("value stored:{}".format(store[i]))
                elif get_data_types[x] == "float":
                    col_list = list(n_df[val])
                    col_l = [s for s in col_list]
                    col_list_array = np.asarray(col_l)
                    rat.SetValueAsDouble(ind, x, col_list_array[row_val])
                else:
                    len_row = len(n_df[val])
                    store_val_st = list(n_df[val])
                    rat.SetValueAsString(ind, x, list(store_val_st))

            print(type(rat.GetTypeOfCol(2)))
        '''
            expected type: <class 'osgeo.gdal.RasterAttributeTable'> 
            if none recheck your rat i,e how you have populated it
        '''

        # print("{}:{}".format(i, value))

        band = attraction_ds.GetRasterBand(1)
        band.SetDefaultRAT(rat)
        band.FlushCache()

        del attraction_ds, band
        print("Successfully joined RAT with csv...")
    else:
        '''
            this is executed if the RAT already exists:
            Population of the created RAT from csv passed works//
            however saving it to the existing raster is a bit of challenge for now//
            a WIP...
            A possible solution is overwriting PAM before RAT...
        '''
        join_csv_with_rat(raster_filename,out_put_file,input_csv)
