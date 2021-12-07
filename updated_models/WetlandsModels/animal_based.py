import manipulate_pixel_values

'''
 Test for generation of rasters as outlined in the wetlands models documentation
 Each function generates a specific output raster as indicated /commented on above/beside it
 output 1 raster is occasioned by the join function, the raster generated used as might be required//
 by subsequent functions 
'''
# look up field as input
# make look up field the raster values
look_up_field_1 = "area 1"
look_up_field_2 = "Expe"
raster_file_name = "data/MAULULC.tif"
output_raster_lookup1 = "lookup1_newRaster.tif"
output_raster_lookup2 = "lookup_2_newRaster.tif"
output_raster_lookup3 = "lookup3_newRaster.tif"
raster_from_input_val = "raster_from_inputVal.tif"
divided_raster_filename = "divided_rasters.tif"

# rat_list = manipulate_pixel_values.get_rat_list(raster_file_name)
'''output 2 raster generated by code below'''
output_raster_2 = manipulate_pixel_values.values_from_lookup(raster_file_name,output_raster_lookup1,"area 1")
'''output 3 raster raster generated by code below'''
# output_raster_3 = manipulate_pixel_values.values_from_lookup(raster_file_name, output_raster_lookup2, "Expe")


'''output 4: multiply raster out put 3 with raster 2'''
# mult_raster = manipulate_pixel_values.multiply_raster("no_data_lookup1_newRaster.tif", "no_data_lookup_2_newRaster.tif", "multiplied_raster.tif")
'''output 5: new raster whose values based on look up 3'''
# output_raster_lookup_3 = manipulate_pixel_values.values_from_lookup(raster_file_name,output_raster_lookup3,"field")
'''output 6: raster whose values divided by input value'''
# output_raster_6 = manipulate_pixel_values.multiply_pixel_by_value("no_data_lookup3_newRaster.tif",raster_from_input_val,10)
'''output 7: raster 4/ raster 6'''
ras_a = "no_data_multiplied_raster.tif"
ras_b = "no_data_raster_from_inputVal.tif"
# output_raster_7 = manipulate_pixel_values.divide_two_rasters(ras_a,ras_b,divided_raster_filename)

