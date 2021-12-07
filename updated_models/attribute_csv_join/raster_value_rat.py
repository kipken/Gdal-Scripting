from osgeo import gdal
import numpy as np
import subprocess
import pandas as pd
import csv
import json

attraction_raster = "data/MAULULC.tif"

'''
    This code reads a raster, gets unique values 
'''
attraction_ds = gdal.Open(attraction_raster, gdal.GA_Update)  # open in update mode with gdal.GA_Update
my_array = np.array(attraction_ds.GetRasterBand(1).ReadAsArray())
values, count = np.unique(my_array, return_counts=True)
print(type(values))
# print(attraction_ds.values())
df = pd.DataFrame({'unique_value': values, 'COUNT': count})

print("{}:{}".format(values, count))

'''
    the code below:
    1. creates an empty raster attribute table
    2. Populates it with values.
    3. stores the attribute info to the raster


'''
# create an empty Raster Attribute Table and populate it using the values, their frequency and their class

attraction_vec = "data/attractionsite_values.csv"
print("Reading raster and csv files....")
ras_ds = gdal.Open(attraction_raster)
vec_ds = gdal.Open(attraction_vec)
n_df = pd.read_csv(attraction_vec)
print(n_df)
# lyr = vec_ds.GetLayer()
geot = ras_ds.GetGeoTransform()
# get fields
print("Extracting the csv fields/ column names")

csv_fields = list(n_df.columns)
unique_field = list(n_df["field"])
get_data_types = []
print(unique_field)
# get data type for csv
print("Getting datatypes for each column....")
for i in range(len(csv_fields)):
    if n_df.iloc[:, i].dtype == "object":
        get_data_types.append("string")
    elif n_df.iloc[:, i].dtype == "int64":
        get_data_types.append("int")
    elif n_df.iloc[:, i].dtype == "float64" or "float32":
        get_data_types.append("float")
print(get_data_types)
print(len(csv_fields))
print("Converting csv fields to an array..")
for n, m in enumerate(csv_fields):
    print(np.asarray(list(n_df[m])))
# print(len(n_df["class"]))

'''dynamic updating of raster attribute table'''

# instantiate an empty raster
print("Instantiating an empty raster attribute table with columns")
rat = gdal.RasterAttributeTable()
rat.CreateColumn('unique_value', gdal.GFT_Integer, gdal.GFU_Generic)
rat.CreateColumn('COUNT', gdal.GFT_Integer, gdal.GFU_Generic)
for i in csv_fields:
    print(i)
    rat.CreateColumn(i, gdal.GFT_String, gdal.GFU_Generic)

print("RAT instantiated")

print(type(rat))

#  populating the raster
print("Populating raster attribute table")
for i, (value, total) in enumerate(zip(values, count)):
    #     print("{}:{}".format(value,con))
    if value not in unique_field:
        print("Values not in unique field of csv")
        break
    else:
        rat.SetValueAsInt(i, 0, int(value))
        rat.SetValueAsInt(i, 1, int(total))
        stop = len(csv_fields) + 2
        for x, val in enumerate(csv_fields):
            print(val)
            if get_data_types[x] == "int":
                store_val = list(n_df[val])
                print(type(store_val))
                store = [ix for ix in store_val]
                store = np.asarray(store)
                print(type(store))
                # len_rows = len(n_df[val])
                # for row in range(len_rows):
                rat.SetValueAsInt(i, x+1, int(store[x]))
            elif get_data_types[x] == "float":
                store_val = list(n_df[val])
                print(type(store_val))
                store = [i for i in store_val]
                store = np.asarray(store)
                print(type(store))

                rat.SetValueAsDouble(i, x+1, int(store[x]))
            else:
                len_row = len(n_df[val])
                store_val_st = list(n_df[val])
                rat.SetValueAsString(i, x + 1, list(store_val_st))

        print(type(rat))
        '''
            expected type: <class 'osgeo.gdal.RasterAttributeTable'> 
            if none recheck your rat i,e how you have populated it
        '''

        print("{}:{}".format(i, value))

band = attraction_ds.GetRasterBand(1)
band.SetDefaultRAT(rat)
band.FlushCache()

del attraction_ds, band
print("Successfully joined RAT with csv...")