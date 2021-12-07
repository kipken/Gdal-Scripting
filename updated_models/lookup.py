from osgeo import gdal
import pandas as pd
import csv
import re

'''initialize your datasets and outputs'''
att_raster = "MAU COMPLEX/MAUBIOMASS.tif"
out_put_csv = "attribute_table.csv"

# Open raster in update mode
rs = gdal.Open(att_raster, gdal.GA_Update)

# try to read the RAT
rb = rs.GetRasterBand(1)
rat = rs.GetRasterBand(1).GetDefaultRAT()
print(type(rat))

print(rat)

# input fields and filter value
'''initialize search field and input value'''
search_field = None
filter_value = None


# check for data_type field/value
def get_search_type(input_value):
    if isinstance(input_value, str):
        field_type = 'string'
    elif isinstance(input_value, int):
        field_type = 'int'
    else:
        field_type = None
    #     value_type = type(filter_value)

    return field_type


print(get_search_type(56))

'''
    read rat, from its fields, define a field to perform  your filter//
    use the filter value to filter info and save the resulting raster
'''


# # convert RAT to csv and perform your filters


def to_csv(rat, filepath):

    with open(filepath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write out column headers
        icolcount = rat.GetColumnCount()
        cols = []
        for icol in range(icolcount):
            cols.append(rat.GetNameOfCol(icol))
        csvwriter.writerow(cols)

        # Write out each row.
        irowcount = rat.GetRowCount()
        for irow in range(irowcount):
            cols = []
            for icol in range(icolcount):
                itype = rat.GetTypeOfCol(icol)
                # if col is an integer
                if itype == gdal.GFT_Integer:
                    value = '%s' % rat.GetValueAsInt(irow, icol)
                # if col is a double
                elif itype == gdal.GFT_Real:
                    value = '%.16g' % rat.GetValueAsDouble(irow, icol)
                # else is a string
                else:
                    value = '%s' % rat.GetValueAsString(irow, icol)
                cols.append(value)
            csvwriter.writerow(cols)


to_csv(rat, out_put_csv)

ncsv = "attribute_table.csv"
lookup_df = pd.read_csv(ncsv)


lookup_df["CLASS"]


'''
    this performs a lookup on a certain df and returns the filtered df based//
    on look up values
'''


def get_lookup_df(lookup_df, lookup_value):
    boolean = []
    for result in lookup_df.CLASS:
        #     print(result)
        if re.search(lookup_value, result):
            boolean.append(False)
        else:
            boolean.append(True)

    lookup_series = pd.Series(boolean)
    new_lookup_df = lookup_df[lookup_series]
    new_lookup_df
    return new_lookup_df


get_lookup_df(lookup_df, "Unclassified")

'''
    Code to append the filtered data from get_lookup_df above//
    to the raster// new raster with attribute from lookup
'''
