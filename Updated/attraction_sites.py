#!/usr/bin/env python
# coding: utf-8

# # <span style ="color:blue">Cultural Recreation and Education Model-Forest </span>

# In[15]:


from osgeo import gdal
import numpy as np
import subprocess
import pandas as pd
import csv
# from rios import rat


# ### Initialize your file paths here

# In[28]:



attractionsite_csv =  "MAU/attractionsite_values.csv"
attraction_raster = "MAU/MAU BIOMASS.tif"
# mau_soc = "MAU/MAU SOIL ORGANIC CARBON.tif"


# ### get your csv file

# In[23]:


attraction_df = pd.read_csv(attractionsite_csv)
attraction_df


# In[31]:


attraction_ds = gdal.Open(attraction_raster,gdal.GA_Update)
myarray = np.array(forest_ds.GetRasterBand(1).ReadAsArray())
# print(attraction_ds.values())


# # read raster file and extract the attribute table as a csv

# get unique values from the raster
attraction_rb = attraction_ds.GetRasterBand(1)
# forest_array = attraction_rb.ReadAsArray()
unique_values = np.unique(attraction_rb.ReadAsArray())

# create a raster attribute table
# rat = gdal.RasterAttributeTable()

# initialize your rat here
forest_rat = forest_rb.GetDefaultRAT()

print(unique_values)


# # Convert RAT to a csv

# In[27]:


def tocsv(rat, filepath):
    with open(filepath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        #Write out column headers
        icolcount=rat.GetColumnCount()
        cols=[]
        for icol in range(icolcount):
            cols.append(rat.GetNameOfCol(icol))
        csvwriter.writerow(cols)

        #Write out each row.
        irowcount = rat.GetRowCount()
        for irow in range(irowcount):
            cols=[]
            for icol in range(icolcount):
                itype=rat.GetTypeOfCol(icol)
                if itype==gdal.GFT_Integer:
                    value='%s'%rat.GetValueAsInt(irow,icol)
                elif itype==gdal.GFT_Real:
                    value='%.16g'%rat.GetValueAsDouble(irow,icol)
                else:
                    value='%s'%rat.GetValueAsString(irow,icol)
                cols.append(value)
            csvwriter.writerow(cols)

raster_csv = tocsv(forest_rat,'raster_csv.csv')
raster_df = pd.read_csv(raster_csv)
# if __name__ == '__main__':
#     ds=gdal.Open(sys.argv[1])
#     rat=ds.GetRasterBand(1).GetDefaultRAT()
#     tocsv(rat, '/path/to/output.csv')


# # Join raster csv with the forest csv using unique id

# In[ ]:


# initialize unique raster value and corresponding value in csv to use for join
raster_unique = ""
csv_unique = ""

merged_dataframe = pd.merge(raster_csv, dataframe4, left_on= raster_unique, right_on= csv_unique, how= "inner")


# # Process the csv back to raster with the added attribute information

'''
    After joining is successful, save the output for further raster calculations
'''

# ### Command line for gdal





