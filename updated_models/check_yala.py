from osgeo import gdal

ras = "Yala_Sentinel2_LULC2016.tif"

attraction_ds = gdal.Open(ras,gdal.GA_Update)
my_array = attraction_ds.GetRasterBand(1).ReadAsArray()
print(my_array.shape)