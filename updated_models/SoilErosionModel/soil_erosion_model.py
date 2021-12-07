from osgeo import gdal, gdalconst
import numpy as np
import os


def read_raster(raster_file_list):
    for i, v in enumerate(raster_file_list):
        ras = gdal.Open(raster_file_list[i])
        noDv = ras.GetRasterBand(1).GetNoDataValue()
        band = ras.GetRasterBand(1)
        my_array = np.array(band.ReadAsArray())

        print("No data for raster {} : {} , shape: {}".format(i, noDv, my_array.shape))


'''
    raster have different shapes
    possible solution..
    1. Resample your rasters to a common resolution 
'''

'''
code below resamples a raster,
one raster with known dimension used to set others to have same size
'''
def resample_rasters(raster_file_list, out_put_name):
    '''
    :param raster_file_list:
    :param out_put_name:
    :return:
    '''
    src_filename = 'MENHMAgome01_8301/mllw.gtx'
    src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    src_geotrans = src.GetGeoTransform()

    # We want a section of source that matches this:
    match_filename = 'F00574_MB_2m_MLLW_2of3.bag'
    match_ds = gdal.Open(match_filename, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize

    # Output / destination
    dst_filename = 'F00574_MB_2m_MLLW_2of3_mllw_offset.tif'
    dst = gdal.GetDriverByName('GTiff').Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform(match_geotrans)
    dst.SetProjection(match_proj)

    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Bilinear)

    del dst  # Flush
    pass


def multiply_multiple_rasters(raster_file_list, out_put_name):
    if not os.path.isdir("raster_multiplied"):
        os.mkdir("raster_multiplied")
    out_put_raster = "raster_multiplied/" + out_put_name
    raster_1 = gdal.Open(raster_file_list[0])
    raster_2 = gdal.Open(raster_file_list[1])
    ras_arr_1 = np.array(raster_1.GetRasterBand(1).ReadAsArray())
    ras_arr_2 = np.array(raster_2.GetRasterBand(1).ReadAsArray())
    new_ras_arr = ras_arr_1 + ras_arr_2
    for i, v in enumerate(raster_file_list):
        if i > 1:
            new_raster = gdal.Open(raster_file_list[i])
            new_arr = np.array(new_raster.GetRasterBand(1).ReadAsArray())
            new_ras_arr = new_ras_arr * new_arr
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(out_put_raster, raster_1.RasterXSize,
                                  raster_1.RasterYSize, 1, gdalconst.GDT_Float32)
    output_raster.GetRasterBand(1).WriteArray(new_ras_arr)
    proj = raster_1.GetProjection()
    geo_ref = raster_1.GetGeoTransform()
    output_raster.SetProjection(proj)
    output_raster.SetGeoTransform(geo_ref)
    translated = "raster_multiplied/" + "no_data_" + out_put_name
    new_raster = gdal.Translate(translated, output_raster, noData=0, outputType=gdalconst.GDT_Float32)
    return new_raster


raster_list = ["results/translate_1.tif","results/translate_2.tif"]

read_raster(raster_list)
# multiply_multiple_rasters(raster_list, "multiplied.tif")
