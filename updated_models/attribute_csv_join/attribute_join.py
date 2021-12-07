from updated_attribute_join import attribute_csv_join

# executing this function example

attraction_raster = "data/FishingRaster.tif"
# attraction_raster = "Yala/Yala_Sentinel2_LULC2016.tif"
attraction_vec = "data/FISH_CSV.csv"
input_field = "field" #as specified by the user
# input field should match the values in the raster
 # the user passes the specific field name from the csv for this example "field" is used
#  trial join
csv = "Reclass/attractionsite values.csv"
raster = "Reclass/MAULULC_RECLASS.tif"
'''for a none existing rat, a join could be performed by passing either {OID /Values}'''
attribute_csv_join(csv, raster, "../data/create_new_rat.tif", "Values", "field")
