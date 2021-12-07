import rasterio
from rasterio.merge import merge
import os
from osgeo import gdal, gdalconst
import numpy as np


def mosaic_with_rasterio(list_files_to_mosaic, output_name):
    os.mkdir("mosaicked_data")
    output_name = "mosaicked_data/" + output_name
    with rasterio.open(list_files_to_mosaic[0]) as src:
        meta = src.meta.copy()

    # The merge function returns a single array and the affine transform info
    arr, out_trans = merge(list_files_to_mosaic)

    meta.update({
        "driver": "GTiff",
        "height": arr.shape[1],
        "width": arr.shape[2],
        "transform": out_trans
    })

    # Write the mosaic raster to disk
    with rasterio.open(output_name, "w", **meta) as dest:
        dest.write(arr)


def mosaic_with_gdal(list_files_to_mosaic, output_name):
    '''look for a way to eliminate the no data values '''
    # len_rasters =  len(list_files_to_mosaic)
    for i, v in enumerate(list_files_to_mosaic):
        driver = gdal.GetDriverByName('GTiff')
        input_raster = gdal.Open(list_files_to_mosaic[i])
        noDv = input_raster.GetRasterBand(1).GetNoDataValue()
        print("No data value for raster {} : {}".format(i, noDv))
    if not os.path.isdir('mosaicked_data'):
        os.mkdir("mosaicked_data")
    output_name = "mosaicked_data/" + output_name
    g = gdal.Warp(output_name, list_files_to_mosaic, format="GTiff",
                  options=["COMPRESS=LZW", "TILED=YES"], dstNodata=0)  # if you want
    g = None


def divide_raster_1(input_ras, output_path, value):
    if not os.path.isdir("divide_raster_1"):
        os.mkdir("divide_raster_1")
    out_put_path = "divide_raster_1/" + output_path
    raster = gdal.Open(input_ras)
    ras_band = raster.GetRasterBand(1)
    raster_arr = np.array(ras_band.ReadAsArray())
    print(raster_arr)
    new_ras_arr = raster_arr / value
    print(new_ras_arr)
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_path, raster.RasterXSize,
                                  raster.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_ras_arr)
    proj = raster.GetProjection()
    geo_ref = raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    translated = "divide_raster_1/" + "nodata_" + output_path
    new_raster = gdal.Translate(translated, output_raster, noData=0, outputType=gdalconst.GDT_Float32)
    return new_raster
    # pass


def raster_times_1(input_file, output_path, input_value):
    if not os.path.isdir("raster_times_1"):
        os.mkdir('raster_times_1')
    out_put_path = "raster_times_1/" + output_path
    raster = gdal.Open(input_file)
    ras_band = raster.GetRasterBand(1)
    raster_arr = np.array(ras_band.ReadAsArray())
    print(raster_arr)
    new_ras_arr = raster_arr * input_value
    print(new_ras_arr)
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_path, raster.RasterXSize,
                                  raster.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_ras_arr)
    proj = raster.GetProjection()
    geo_ref = raster.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    translated = "raster_times_1/" + "nodata_" + output_path
    new_raster = gdal.Translate(translated, output_raster, noData=0, outputType=gdalconst.GDT_Float32)
    return new_raster


'''performs an addition of multiple files'''


def raster_calculator(my_raster_list, out_put_name):
    if not os.path.isdir("raster_calculator"):
        os.mkdir("raster_calculator")
    out_put_raster = "raster_calculator/" + out_put_name
    raster_1 = gdal.Open(my_raster_list[0])
    raster_2 = gdal.Open(my_raster_list[1])
    ras_arr_1 = np.array(raster_1.GetRasterBand(1).ReadAsArray())
    ras_arr_2 = np.array(raster_2.GetRasterBand(1).ReadAsArray())
    cum_ras_arr = ras_arr_1 + ras_arr_2
    for i, v in enumerate(my_raster_list):
        if i > 1:
            new_raster = gdal.Open(my_raster_list[i])
            new_arr = np.array(new_raster.GetRasterBand(1).ReadAsArray())
            cum_ras_arr = cum_ras_arr + new_arr
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_raster, raster_1.RasterXSize,
                                  raster_1.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(cum_ras_arr)
    proj = raster_1.GetProjection()
    geo_ref = raster_1.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    translated = "raster_calculator/" + "no_data_" + out_put_name
    new_raster = gdal.Translate(translated, output_raster, noData=0, outputType=gdalconst.GDT_Float32)
    return new_raster


# my_list = [1, 2, 3, 4]
# raster_calculator(my_list)

"""gdal performs well for this"""
raster = ["WoodProduct_Data/AGB_Kariba.tif", "WoodProduct_Data/LULCFOREST_Kariba.tif"]
# mosaic_with_rasterio(raster,"mosaicked.tif")
# mosaic_with_gdal(raster, "mosaicked_gdal.tif")
my_ras = "mosaicked_data/mosaicked_gdal.tif"
raster_for_multiplication = "divide_raster_1/nodata_divide_raster1.tif"
# divide_raster_1(my_ras,"divide_raster1.tif",10)
raster_times_1(raster_for_multiplication, "mutiplied_ras_1.tif", 10)
# # attraction_ds = gdal.Open(my_ras, gdal.GA_Update)
# # my_array = attraction_ds.GetRasterBand(1).ReadAsArray()
raster_list = [my_ras, "raster_times_1/nodata_mutiplied_ras_1.tif", "divide_raster_1/nodata_divide_raster1.tif"]
raster_calculator(raster_list, "multiple_added.tif")
# print(my_array[0])
