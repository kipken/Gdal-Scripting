import os.path
import subprocess
import sys
from os import path
from osgeo import gdal, gdalconst, ogr
import fiona
import numpy as np
from osgeo.utils import gdal_calc
import geopandas as gpd

ras_1_out = "results/translate_1.tif"
ras_2_out = "results/translate_2.tif"

ras_1_clip = "results/clip_1.tif"
ras_2_clip = "results/clip_2.tif"

# no_data_value = 3.41282306073738


def create_new_raster(new_array, input_raster_name, output_file_name):
    '''
    :param new_array: array computed from cell statistics
    :param input_raster_name: this is the filename of the raster, it should have a raster attribute table
    :param output_file_name: the output path to store the created raster
    :return: returns a new raster
    '''

    height, width = new_array.shape
    driver = gdal.GetDriverByName('GTiff')
    input_raster = gdal.Open(input_raster_name)
    my_array = np.array(input_raster.GetRasterBand(1).ReadAsArray())
    print(my_array)
    values, count = np.unique(my_array, return_counts=True)
    # print(list(values))
    # create raster
    output_raster = driver.Create(output_file_name, width,
                                  height, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_array)
    # output_raster.GetRasterBand(1).SetNoDataValue(3.40282306073738*3)
    proj = input_raster.GetProjection()
    geo_ref = input_raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    translated = "statistics/no_data_statistics.tif"
    ndv = 3.40282306073738 * 3
    new_raster = gdal.Translate(translated, output_raster, noData=ndv, outputType=gdalconst.GDT_Float64)
    return output_raster


def multiply_multiple_rasters(raster_file_list, out_put_name):
    if not os.path.isdir("raster_multiplied"):
        os.mkdir("raster_multiplied")
    out_put_raster = "raster_multiplied/" + out_put_name
    raster_1 = gdal.Open(raster_file_list[0])
    raster_2 = gdal.Open(raster_file_list[1])
    prod = "raster_multiplied/raster_multiplied_gdal.tif"
    gdal_calc.Calc("A*B", A=raster_file_list[0], B=raster_file_list[1],
                   outfile="raster_multiplied/raster_multiplied_gdal.tif",
                   overwrite=True)
    for i, v in enumerate(raster_file_list):
        if i > 1:
            gdal_calc.Calc("A*B", A=prod, B=v, outfile="raster_multiplied/raster_multiplied_gdal.tif",
                           overwrite=True)


def translate_raster(ras_list):
    # create directory for storing resampled data
    if not os.path.isdir("resampled_rasters"):
        os.mkdir("resampled_rasters")
    # transalate rasters and store
    for i, prev in enumerate(ras_list):
        ras_t = gdal.Open(prev)
        nd = ras_t.GetRasterBand(1).GetNoDataValue()
        ras_translated = "resampled_rasters/" + "translate_" + str(i) + ".tif"
        gdal.Translate(ras_translated, prev, noData=0, outputType=gdalconst.GDT_Float64)


def resample_raster(translated_ras_list):
    # get x and y origins for the two rasters
    x_origin = 0
    y_origin = 0
    c = 1
    # intersection = None
    x_min = 0
    x_max = 0
    y_min = 0
    y_max = 0
    x_off = 0
    y_off = 0
    x_count = 0
    y_count = 0
    print(".....................................................................................")
    for idx, prev in enumerate(translated_ras_list):
        for j, curr in enumerate(translated_ras_list[c:]):
            # trans_ras_prev = "resampled/" + "translate_" + str(idx) + ".tif"
            # trans_ras_curr = "resampled/" + "translate_" + str(j) + ".tif"
            print(idx, " ", prev, " ", curr)
            prev_ras = gdal.Open(prev)
            curr_ras = gdal.Open(curr)
            print(prev_ras.ReadAsArray())
            # this gets the properties of the raster i.e the upper left origin(x and y) & lower right origin(x and y)
            # for both rasters
            gt_1 = prev_ras.GetGeoTransform()
            # ulx, xres, xskew, uly, yskew, yres = ras_1.GetGeoTransform()
            gt_2 = curr_ras.GetGeoTransform()
            r_1 = [gt_1[0], gt_1[3], (gt_1[0] + (gt_1[1] * prev_ras.RasterXSize)),
                   (gt_1[3] + (gt_1[5] * prev_ras.RasterYSize))]
            r_2 = [gt_2[0], gt_2[3], (gt_2[0] + (gt_2[1] * curr_ras.RasterXSize)),
                   (gt_2[3] + (gt_2[5] * curr_ras.RasterYSize))]
            intersection = [max(r_1[0], r_2[0]), min(r_1[1], r_2[1]), min(r_1[2], r_2[2]), max(r_1[3], r_2[3])]
            x_min = intersection[0]
            x_max = intersection[2]
            y_min = intersection[3]
            y_max = intersection[1]
            pixel_width = gt_1[1]
            pixel_height = gt_1[5]
            x_off = int((x_min - x_origin) / pixel_width)
            y_off = int((y_origin - y_max) / pixel_width)
            x_count = int((x_max - x_min) / pixel_width)
            y_count = int((y_max - y_min) / pixel_width)
            # print('gt_1', gt_1)
            # print('gt_2', gt_2)
            if gt_1[0] < gt_2[0]:
                x_origin = gt_2[0]
            else:
                x_origin = gt_1[0]

            if gt_1[3] < gt_2[3]:
                y_origin = gt_1[3]
            else:
                y_origin = gt_2[3]

        c += 1
    print("...........................................................................................................")
    # write array and store

    for ind, ras in enumerate(ras_list):
        rast = gdal.Open(ras)
        raster_arr = np.array(rast.ReadAsArray(x_off, y_off, x_count, y_count))
        ras_nd = rast.GetRasterBand(1).GetNoDataValue()
        no_data_value = -3.402823
        raster_arr[raster_arr == ras_nd] = no_data_value
        resampled_out_put = "resampled_rasters/" + "resampled_" + str(ind) + ".tif"
        ras_1_output = gdal.GetDriverByName('GTiff').Create(resampled_out_put, x_count, y_count, 1,
                                                            gdalconst.GDT_Float64)
        ras_1_output.GetRasterBand(1).WriteArray(raster_arr)
        ras_1_output.GetRasterBand(1).SetNoDataValue(no_data_value)
        proj = rast.GetProjection()
        geo_ref = rast.GetGeoTransform()
        ras_1_output.SetProjection(proj)
        ras_1_output.SetGeoTransform(geo_ref)
        translated = "resampled_rasters/"+"final_translated_"+str(ind)+".tif"
        new_raster = gdal.Translate(translated, ras_1_output, noData=no_data_value,
                                    outputType=gdalconst.GDT_Float32)

        ras_1_output = None

    print(x_origin, y_origin)
    print("x_off:", x_off, "y_off:", y_off, "x_count:", x_count, "y-couint:", y_count)


'''used to get the area in hectares used for subsequent raster manipulation'''


def get_shapefile_value(shapefile, col_to_use):
    data = gpd.read_file(shapefile)
    area = data[col_to_use]
    print(data['areaha'])
    return area
    # print(layer.GetFeature(0))


def zonal_statistics(raster_list):
    # all_arrays = None
    driver = gdal.GetDriverByName('GTiff')
    input_raster = gdal.Open(raster_list[0])
    # no_data = 3.41282306073738
    for i, raster in enumerate(raster_list):
        rst_obj = gdal.Open(raster)
        nodata_value = rst_obj.GetRasterBand(1).GetNoDataValue()
        print("No data value", nodata_value)
        array = rst_obj.ReadAsArray()
        print("Raster array", array)
        # from the individual raster get the no data value and assign all no data values to
        array[array == nodata_value] = 0
        array = np.expand_dims(array, 2)
        if i == 0:
            all_arrays = array
        else:
            all_arrays = np.concatenate((all_arrays, array), axis=2)
    raster_mean = np.sum(all_arrays, axis=2) / len(raster_list)
    print("raster mean: ", raster_mean)
    if not os.path.isdir("statistics"):
        os.mkdir("statistics")
    output_file_name = "statistics/zonal_stats.tif"
    # create raster
    output_raster = driver.Create(output_file_name, input_raster.RasterXSize,
                                  input_raster.RasterYSize, 1, gdalconst.GDT_Float64)
    output_raster.GetRasterBand(1).WriteArray(raster_mean)
    proj = input_raster.GetProjection()
    geo_ref = input_raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    print("No data out put ras", output_raster.GetRasterBand(1).GetNoDataValue())
    final_dir = "statistics/final_stats"
    if not os.path.exists(final_dir):
        os.mkdir(final_dir)
    translated = final_dir + "/" + "zonal_stats_noDAta.tif"
    new_raster = gdal.Translate(translated, output_raster, noData=0, outputType=gdalconst.GDT_Float64)
    print("No data new ras", new_raster.GetRasterBand(1).GetNoDataValue())
    return new_raster


'''multiplies a given list of raster and outputs product raster'''


def run_multiply_raster(rat_list, out_put):
    '''

    :param rat_list: this is a list of rasters either Land cover(
    :return:
    '''
    if len(ras_list) <= 2:
        resample_raster(ras_list[0], ras_list[1])
    else:
        print("processing first batch...")
        resample_raster(ras_list[0], ras_list[1])
        for i in range(len(ras_list)):
            if i > 1:
                print("processing subsequent rasters, raster {}".format(i))
                resample_raster(prod, ras_list[i])


def multiply_raster_by_shapefile_value(input_ras, vector_file, shp_field, out_put_path):
    value = get_shapefile_value(vector_file, shp_field)
    if not os.path.isdir("multiplied_from_shapefile_value"):
        os.mkdir('multiplied_from_shapefile_value')
    out_put_path = "multiplied_from_shapefile_value/" + out_put_path
    raster = gdal.Open(input_ras)
    ras_band = raster.GetRasterBand(1)
    raster_arr = np.array(ras_band.ReadAsArray())
    print(raster_arr)
    new_ras_arr = raster_arr * value
    print(new_ras_arr)
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_path, raster.RasterXSize,
                                  raster.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_ras_arr)


def divide_raster_by_shapefile_value(input_ras, shp, shapefile_field, output_path):
    divide_value = get_shapefile_value(shp, shapefile_field)
    div_ratio = 10000 / divide_value
    if not os.path.isdir("divided_by_shapefile_value"):
        os.mkdir('divided_by_shapefile_value')
    out_put_path = "divided_by_shapefile_value/" + output_path
    raster = gdal.Open(input_ras)
    ras_band = raster.GetRasterBand(1)
    raster_arr = np.array(ras_band.ReadAsArray())
    print(raster_arr)
    new_ras_arr = raster_arr * div_ratio
    print(new_ras_arr)
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_path, raster.RasterXSize,
                                  raster.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_ras_arr)


def minus_alc_nc_rasters(alc_raster, nc_raster, out_put_ras):
    no_data_value = -3.402823
    if not os.path.isdir('results/minus'):
        os.mkdir('results/minus')
    # Translate rasters to set format
    gdal.Translate("results/minus/translated_1.tif", alc_raster, outputType=gdalconst.GDT_Float32)
    gdal.Translate("results/minus/translated_2.tif", nc_raster, outputType=gdalconst.GDT_Float32)

    ras_1 = gdal.Open(ras_1_out)
    ras_2 = gdal.Open(ras_2_out)

    gt_1 = ras_1.GetGeoTransform()
    gt_2 = ras_2.GetGeoTransform()

    # Conditional to select the correct origin

    if gt_1[0] < gt_2[0]:
        gt_3 = gt_2[0]
    else:
        gt_3 = gt_1[0]

    if gt_1[3] < gt_2[3]:
        gt_4 = gt_1[3]
    else:
        gt_4 = gt_2[3]

    x_origin = gt_3
    y_origin = gt_4
    pixel_width = gt_1[1]
    pixel_height = gt_1[5]

    r_1 = [gt_1[0], gt_1[3], (gt_1[0] + (gt_1[1] * ras_1.RasterXSize)), (gt_1[3] + (gt_1[5] * ras_1.RasterYSize))]
    r_2 = [gt_2[0], gt_2[3], (gt_2[0] + (gt_2[1] * ras_2.RasterXSize)), (gt_2[3] + (gt_2[5] * ras_2.RasterYSize))]
    intersection = [max(r_1[0], r_2[0]), min(r_1[1], r_2[1]), min(r_1[2], r_2[2]), max(r_1[3], r_2[3])]

    x_min = intersection[0]
    x_max = intersection[2]
    y_min = intersection[3]
    y_max = intersection[1]

    # Specify offset and rows and columns to read.
    x_off = int((x_min - x_origin) / pixel_width)
    y_off = int((y_origin - y_max) / pixel_width)
    x_count = int((x_max - x_min) / pixel_width)
    y_count = int((y_max - y_min) / pixel_width)

    ras_1_array = np.array(ras_1.ReadAsArray(x_off, y_off, x_count, y_count))
    ras_2_array = np.array(ras_2.ReadAsArray(x_off, y_off, x_count, y_count))

    ras_1_nd = ras_1.GetRasterBand(1).GetNoDataValue()
    ras_2_nd = ras_2.GetRasterBand(1).GetNoDataValue()

    ras_1_array[ras_1_array == ras_1_nd] = no_data_value
    ras_2_array[ras_2_array == ras_2_nd] = no_data_value

    nd_product = no_data_value * no_data_value

    product = ras_1_array * ras_2_array

    ras_1_output = gdal.GetDriverByName('GTiff').Create(ras_1_clip, x_count, y_count, 1, gdalconst.GDT_Float32)
    ras_1_output.GetRasterBand(1).WriteArray(ras_1_array)
    ras_1_output.GetRasterBand(1).SetNoDataValue(no_data_value)
    proj = ras_1.GetProjection()
    geo_ref = ras_1.GetGeoTransform()
    ras_1_output.SetProjection(proj)
    ras_1_output.SetGeoTransform(geo_ref)

    ras_1_output = None

    ras_2_output = gdal.GetDriverByName('GTiff').Create(ras_2_clip, x_count, y_count, 1, gdalconst.GDT_Float32)
    ras_2_output.GetRasterBand(1).WriteArray(ras_2_array)
    ras_2_output.GetRasterBand(1).SetNoDataValue(no_data_value)
    proj = ras_2.GetProjection()
    geo_ref = ras_2.GetGeoTransform()
    ras_2_output.SetProjection(proj)
    ras_2_output.SetGeoTransform(geo_ref)

    ras_2_output = None
    out_put_ras = 'results/minus/' + out_put_ras
    subprocess.call(
        [sys.executable, 'venv/Scripts/gdal_calc.py',
         '-A', ras_1_clip, '-B', ras_2_clip, '--extent=intersect',
         '--outfile=' + out_put_ras, '--type=Float32', '--overwrite',
         '--calc=A.astype(float)-B.astype(float)'])


ras1 = "data/Cfactor_ALC.tif"
ras2 = "data/Kfactor_ALC.tif"
ras_list = [ras1, ras2, "data/LSfactor_ALC.tif", "data/Pfactor_ALC.tif", "data/Rfactor_ALC.tif"]
translated_list = ["resampled_rasters/translate_0.tif", "resampled_rasters/translate_1.tif",
                   "resampled_rasters/translate_2.tif",
                   "resampled_rasters/translate_3.tif", "resampled_rasters/translate_4.tif"]
print(len(ras_list))
prod = "raster_multiplied_gdal.tif"
# tweak the raster to the same shape using below translate and resample functions
translate_raster(ras_list)
resample_raster(translated_list)

# the list below is the final clean rasters to be used for zonal statistics, has same shape
resamp_ras = ["resampled_rasters/resampled_0.tif", "resampled_rasters/resampled_1.tif",
              "resampled_rasters/resampled_2.tif",
              "resampled_rasters/resampled_3.tif", "resampled_rasters/resampled_4.tif"]
multiply_multiple_rasters(resamp_ras, "mul_r.tif")
zonal_statistics(resamp_ras)
