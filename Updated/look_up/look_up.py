from osgeo import gdal
import pandas as pd
import numpy as np

'''
    Two functions: create_new_raster() and addRatToRaster()
    
'''
# file = "../data/"
file_name = "../data/MAULULC.tif"


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


def get_rat_list(input_file_name):
    print("Opening the image in update mode....")
    input_ras = gdal.Open(input_file_name, gdal.GA_Update)
    input_band = input_ras.GetRasterBand(1)
    input_rat = input_band.GetDefaultRAT()
    # get length of cols and rows
    col_len = input_rat.GetColumnCount()
    row_len = input_rat.GetRowCount()
    # append col names
    print("Fetching column names/fields from input RAT...")
    column_names = []

    for i in range(col_len):
        column_names.append(input_rat.GetNameOfCol(i))
    # get field types from RAT
    print("Getting fields types of specific fields from RAT")
    col_types = []
    for i, v in enumerate(column_names):
        if input_rat.GetTypeOfCol(i) == gdal.GFT_String:
            col_types.append("string")
        elif input_rat.GetTypeOfCol(i) == gdal.GFT_Real:
            col_types.append("double")
        elif input_rat.GetTypeOfCol(i) == gdal.GFT_Integer:
            col_types.append("integer")
    # create new rat
    print("Creating an empty RAT & appending data")
    output_rat = gdal.RasterAttributeTable()
    for ix, val in enumerate(column_names):
        if col_types[ix] == "integer":
            output_rat.CreateColumn(val, gdal.GFT_Integer, gdal.GFU_Generic)
        elif col_types[ix] == "double":
            output_rat.CreateColumn(val, gdal.GFT_Real, gdal.GFU_Generic)
        else:
            output_rat.CreateColumn(val, gdal.GFT_String, gdal.GFU_Generic)
    # create a rat list
    rat_list = []
    for idx, vl in enumerate(col_types):
        field_name = column_names[idx]
        val_list = []
        for row in range(row_len):
            if col_types[idx] == "integer":
                # col_val = [rat.GetValueAsInt(row, idx)]
                field_name = column_names[idx]
                # print(new_val)
                val_list.append(input_rat.GetValueAsInt(row, idx))
            elif col_types[idx] == "double":
                field_name = column_names[idx]
                # col_val =[rat.GetValueAsDouble(row,idx)]
                # print(input_rat.GetValueAsDouble(row, idx))
                val_list.append(input_rat.GetValueAsDouble(row, idx))
            elif col_types[idx] == "string":
                field_name = column_names[idx]
                # col_val =[rat.GetValueAsString(row,idx)]
                val_list.append(input_rat.GetValueAsString(row, idx))
        rat_list.append(val_list)
    return column_names, col_types, rat_list


def single_field_manipulation(processed_rat, new_ras, look_up_field, input_value):

    column_names = processed_rat[0]
    col_types = processed_rat[1]
    rat_list = processed_rat[2]
    row_len = len(rat_list[0])
    look_up_index = None
    for j, col_name in enumerate(column_names):
        if col_name == look_up_field:
            look_up_index = j
    output_rat = gdal.RasterAttributeTable()
    for ix, val in enumerate(column_names):
        if col_types[ix] == "integer":
            output_rat.CreateColumn(val, gdal.GFT_Integer, gdal.GFU_Generic)
        elif col_types[ix] == "double":
            output_rat.CreateColumn(val, gdal.GFT_Real, gdal.GFU_Generic)
        else:
            output_rat.CreateColumn(val, gdal.GFT_String, gdal.GFU_Generic)

    edited_col = [rat_list[look_up_index][i] / input_value for i in range(row_len)]
    rat_list[look_up_index] = edited_col
    # populate the RAT
    '''insert the code for populating the raster attribute info using final app list'''

    for ind in range(row_len):
        for x, val in enumerate(column_names):

            if col_types[x] == "integer":

                output_rat.SetValueAsInt(ind, x, int(rat_list[x][ind]))
                # print("value stored:{}".format(store[i]))
            elif col_types[x] == "double":
                output_rat.SetValueAsDouble(ind, x, rat_list[x][ind])
            else:
                output_rat.SetValueAsString(ind, x, list(rat_list[x][ind]))

    print(rat_list)
    print("finished creating new RAT...")
    print(output_rat)
    band = new_ras.GetRasterBand(1)

    band.SetDefaultRAT(output_rat)
    band.FlushCache()
    del new_ras, band
    print("Successully created new raster....")


# create a new raster by performing a division of specified columns from RAT
'''
code below implements:
Function 6: Divide-allows the Output 4 to be divided by output 2 //
(i.e., Output 2 is the numerator and output 4 is the denominator
'''


def multi_field_division(processed_rat, new_ras, look_up_1, look_up_2):
    '''

    :param processed_rat: pass the function -- get_rat_list(filename)
    :param new_ras: from function create new raster
    :param look_up_1: input1 from user or field selected from RAT
    :param look_up_2: input2 from user or field selected from RAT
    :return: None
    '''
    col_names = processed_rat[0]
    col_types = processed_rat[1]
    rat_col_val = processed_rat[2]
    look_up_index_1 = None
    look_up_index_2 = None
    for j, col_name in enumerate(col_names):
        if col_name == look_up_1:
            look_up_index_1 = j
        elif col_name == look_up_2:
            look_up_index_2 = j
    # append new_col_name
    col_names.append("computed field")
    # append new col type to col_types list
    col_types.append("double")
    # divide values and append them to rat_col_val
    look_up_1_val = rat_col_val[look_up_index_1]
    look_up_2_val = rat_col_val[look_up_index_2]
    new_field_vals = [round(i / j, 2) for i, j in zip(look_up_1_val, look_up_2_val)]

    # get number of rows
    row_len = len(rat_col_val[0])
    # append new field list to existing rat list
    rat_col_val.append(new_field_vals)

    # create rat
    output_rat = gdal.RasterAttributeTable()
    for ix, val in enumerate(col_names):
        if col_types[ix] == "integer":
            output_rat.CreateColumn(val, gdal.GFT_Integer, gdal.GFU_Generic)
        elif col_types[ix] == "double":
            output_rat.CreateColumn(val, gdal.GFT_Real, gdal.GFU_Generic)
        else:
            output_rat.CreateColumn(val, gdal.GFT_String, gdal.GFU_Generic)
    # populate values to it
    for ind in range(row_len):
        for x, val in enumerate(col_names):

            if col_types[x] == "integer":

                output_rat.SetValueAsInt(ind, x, int(rat_col_val[x][ind]))
                # print("value stored:{}".format(store[i]))
            elif col_types[x] == "double":
                output_rat.SetValueAsDouble(ind, x, rat_col_val[x][ind])
            else:
                output_rat.SetValueAsString(ind, x, list(rat_col_val[x][ind]))
    # set default rat of new raster as created rat
    band = new_ras.GetRasterBand(1)

    band.SetDefaultRAT(output_rat)
    band.FlushCache()
    del new_ras, band
    print("Successully created new raster....")


# sample test

new_ras = create_new_raster(file_name, "new_ras.tif")
rat = new_ras.GetRasterBand(1).GetDefaultRAT()
# print(get_rat_list(file_name)[0])
processed_rat = get_rat_list(file_name)
# column_names = get_rat_list(file_name)[0]
# column_types = get_rat_list(file_name)[1]
# rat_list = get_rat_list(file_name)[2]
multi_field_division(processed_rat, new_ras, "area 1", "Expe")
# print(processed_rat[0])
# single_field_manipulation(processed_rat, new_ras, "area 1", 10)
# print(addRatToRaster(file_name, new_ras, "area 1", 10))
