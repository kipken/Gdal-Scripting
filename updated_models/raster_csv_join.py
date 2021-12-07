#!/usr/bin/env python
# coding: utf-8
#!/usr/bin/env python
# coding: utf-8

from osgeo import gdal
import numpy as np
import subprocess
import pandas as pd
import csv


# ### Initialize your file paths here

attractionsite_csv =  "attractionsite values.csv"
attraction_raster = "MAU BIOMASS.tif"
attraction_df = pd.read_csv(attractionsite_csv)

# using .unique() returns an array of the specified field
unique_csv_value = attraction_df.field.unique()

# read raster with gdal
attraction_ds = gdal.Open(attraction_raster,gdal.GA_Update)
myarray = np.array(attraction_ds.GetRasterBand(1).ReadAsArray())

# change the array to a dataframe
df = pd.DataFrame(myarray)
print(df)

# # read raster file and extract the attribute table as a csv

attraction_rb = attraction_ds.GetRasterBand(1)
print(attraction_rb)


# get unique values from the band

raster_unique_values = np.unique(attraction_rb.ReadAsArray())
raster_unique_values = raster_unique_values.tolist()


# # Create and populate the attraction RAT

attraction_rat = attraction_rb.GetDefaultRAT()
attraction_rat.CreateColumn('VALUE', gdal.GFT_Integer, gdal.GFU_Generic)
attraction_rat.CreateColumn('LANDUSE', gdal.GFT_String, gdal.GFU_Generic)

for i in range(len(raster_unique_values)):
    rat.SetValueAsInt(i, 0, raster_unique_values[i])
    rat.SetValueAsString(i, 1, unique_csv_value[i])

# bind the joined rat with attraction band 
attraction_rb.SetDefaultRAT(attraction_rat)

# Close the dataset and persist the RAT
attraction_ds = None


'''
	Save the raster EOF.....
'''







