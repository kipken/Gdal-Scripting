from osgeo import gdal
import numpy as np
import sys


def get_rat_list(input_file_name):
    '''
    :param input_file_name: the input file_name a raster with RAT
    '''

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


def change_pixel_values(file_name, output_file_name, look_up_field, input_val, look_up_field_2=None):
    '''

    :param file_name: Name of the raster to manipulate from(should have an attribute table)
    :param output_file_name: output path and file name for you generated raster
    :param look_up_field: this is the first look up field to look up from
    :param input_val: dtype--int, value for manipulating look up field
    :param look_up_field_2: the second field to be looked at
    :return: a raster with manipulated pixel values
    '''
    rat_list = get_rat_list(file_name)
    # get rat list values
    rat_col_names = rat_list[0]
    rat_col_types = rat_list[1]
    rat_col_val = rat_list[2]

    driver = gdal.GetDriverByName('GTiff')
    input_raster = gdal.Open(file_name)
    # get no data value from the band and assign it to zero
    noDv = input_raster.GetRasterBand(1).GetNoDataValue()
    band = input_raster.GetRasterBand(1)
    band_a = band.ReadAsArray()
    band_a[band_a == noDv] = 0
    band_a_cpy = band_a.copy()

    translated = "manipulated_pixel_noDAta.tif"
    my_array = np.array(band_a_cpy)
    values, count = np.unique(my_array, return_counts=True)
    # for i in my_array:
    #     print(i)
    print(my_array.shape)
    print(type(my_array))
    values, count = np.unique(my_array, return_counts=True)
    print(values)
    new_arr = []
    list_val = values.tolist()
    list_val.remove(0)
    print(list_val)
    print(rat_col_val)
    print(rat_col_names)
    # get index for look up field
    if look_up_field_2 is None:
        print("Getting values for look up 1")
        look_up_index = None
        for ix, col_name in enumerate(rat_col_names):
            if col_name == look_up_field:
                look_up_index = ix

        # print(rat_col_names)
        # print(look_up_index)
        # map rat list
        col_to_use = rat_col_val[look_up_index]
        print(col_to_use)
        man_val = [round(i / input_val, 2) for i in col_to_use]
        print(man_val)
    else:
        print("Getting new values from the two look ups passed")
        look_up_ind1 = None
        look_up_ind2 = None
        # print(rat_col_names)
        for i, c_name in enumerate(rat_col_names):
            if c_name == look_up_field:
                look_up_ind1 = i
            elif c_name == look_up_field_2:
                look_up_ind2 = i
        # print(look_up_ind1)
        col1 = rat_col_val[look_up_ind1]
        col2 = rat_col_val[look_up_ind2]
        man_val = [round(j / i, 2) for i, j in zip(col1, col2)]

    # zero value in list values is the no data class

    # man_val = [1, 5, 8, 9, 7, 3.1, 6, 11, 4]
    total_read = 0

    for i, arr in enumerate(my_array):
        new_val = []
        for val in my_array[i]:
            # [for ix,vl in enumerate()]
            for ix, vl in enumerate(man_val):
                if list_val[ix] == val:
                    val = vl
            new_val.append(val)
        new_arr.append(new_val)
        total_read += 1

        percentage_done = round((total_read / my_array.shape[0]) * 100, 0)
        # data = "changing pixel values, Percentage : %d percent done" % percentage_done
        # sys.stdout.write("\r\x1b[K" + data.__str__())
        # sys.stdout.flush()
        print("changing pixel values : {} % done".format(percentage_done))

    new_arr = np.array(new_arr, dtype=float)
    values, count = np.unique(new_arr, return_counts=True)
    print(values)
    # create raster
    output_raster = driver.Create(output_file_name, input_raster.RasterXSize,
                                  input_raster.RasterYSize, 1)
    output_raster.GetRasterBand(1).WriteArray(new_arr)
    proj = input_raster.GetProjection()
    geo_ref = input_raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    new_raster = gdal.Translate(translated, output_raster, noData=0)
    return new_raster

file_name = "./data/MAULULC.tif"
output_file_name = "manipulated_pixels.tif"
'''
running this for function 3 i.e one field only, the last look up field param is ommitted//
when manipulating two fields, all params are passed to the function, use default 10 for 
'''
change_pixel_values(file_name, output_file_name, "area 1", 10,"Expe")
