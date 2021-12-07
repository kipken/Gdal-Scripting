from osgeo import gdal
import numpy as np
import subprocess
import pandas as pd
import csv
import json

attractionsite_csv = "MAU/attractionsite_values.csv"
attraction_raster = "MAU COMPLEX/MAUBIOMASS.tif"
# mau_soc = "MAU/MAU SOIL ORGANIC CARBON.tif"
# read csv
attraction_df = pd.read_csv(attractionsite_csv)
print(attraction_df)

'''
    This code reads a raster, gets unique values 
'''

attraction_ds = gdal.Open(attraction_raster, gdal.GA_Update)  # open in update mode with gdal.GA_Update
my_array = np.array(attraction_ds.GetRasterBand(1).ReadAsArray())
values, count = np.unique(my_array, return_counts=True)

# print(attraction_ds.values())
df = pd.DataFrame({'unique_value': values, 'COUNT': count})

print("{}:{}".format(values, count))

# create a list of unique fields from the csv file

class_map_keys = class_map.keys()
csv_fields = []
for i in class_map_keys:
    csv_fields.append(i)

'''
    The dictionary below is an example of how the csv will be converted //
    allows for easier mapping with the raster attribute//
    currently it works, it can save a csv from RAT + csv info
'''
class_map = {
    1: 'Evergreen Needleleaf Forests',
    2: 'Evergreen Broadleaf Forests',
    3: 'Deciduous Needleleaf Forests',
    4: 'Deciduous Broadleaf Forests',
    5: 'Mixed Forests',
    6: 'Closed Shrublands',
    7: 'Open Shrublands',
    8: 'Woody Savannas',
    9: 'Savannas',
    10: 'Grasslands'
}
# map the raster df with the dictionary generated from csv above
df['CLASS'] = df['unique_value'].map(class_map)

# store the raster attribute table as a csv
df.to_csv('raster_attribute_table.csv', index_label='OID')

'''
    the code below:
    1. creates an empty raster attribute table
    2. Populates it with values.
    3. stores the attribute info to the raster
    
    Error:  still fixing the populating part of the attribute 
'''
# create an empty Raster Attribute Table and populate it using the values, their frequency and their class
rat = gdal.RasterAttributeTable()
rat.CreateColumn('unique_value', gdal.GFT_Integer, gdal.GFU_Generic)
rat.CreateColumn('COUNT', gdal.GFT_Integer, gdal.GFU_Generic)
rat.CreateColumn('CLASS', gdal.GFT_String, gdal.GFU_Generic)
# i=0
print("{}:{}".format(values, count))
for i, (value, total) in enumerate(zip(values, count)):
    #     print("{}:{}".format(value,con))
    if value not in csv_fields:
        print("value {} not found in csv fields.".format(value))
        break
    else:
        rat.SetValueAsInt(i, 0, int(value))
        rat.SetValueAsInt(i, 1, int(coun))
        print(type(rat)) 
        '''
            expected type: <class 'osgeo.gdal.RasterAttributeTable'> 
            if none recheck your rat i,e how you have populated it
        '''

        print("{}:{}".format(i,value))

        rat.SetValueAsString(i, 2, class_map[value])

# save the raster atttribute table to the band (assume ds is the gdal DataSet)
band = attraction_ds.GetRasterBand(1)
band.SetDefaultRAT(rat)
band.FlushCache()

del attraction_ds, band
'''
    the raster attribute data stored in: MAUBIOMASS.tif.aux.xml,
'''

