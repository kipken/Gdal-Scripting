from updated_attribute_join import attribute_csv_join

# executing this function example

attraction_raster = "data/MAULULC.tif"
# attraction_raster = "Yala/Yala_Sentinel2_LULC2016.tif"
attraction_vec = "data/attractionsite_values.csv"
input_field = "field" #as specified by the user
# input field should match the values in the raster
 # the user passes the specific field name from the csv for this example "field" is used 
attribute_csv_join(attraction_vec,attraction_raster,"create_new_rat.tif","field")
