# Python 2 and 3 cross-compatibility:
from __future__ import print_function, division, unicode_literals, absolute_import
from builtins import (bytes, str, int, dict, object, range, map, filter, zip, round, pow, open)
from future.utils import (iteritems, itervalues)
from past.builtins import basestring

from .accessor import accessor

import pandas as pd
import numpy as np

@accessor("nvspl")
def nvspl(nvsplFileEntry, params= (None, None, 1)):
    timestamps, columns, index_index = params

    df = pd.read_csv(str(nvsplFileEntry),
                     engine= 'c',
                     # sep= ',',
                     parse_dates= True,
                     index_col= index_index,
                     infer_datetime_format= True,
                     usecols= columns
                     )

    # Make column names slightly nicer
    df.index.name = "date"
    renamedColumns = { column: column.replace('H', '').replace('p', '.') for column in df.columns if re.match(r"H\d+p?\d*", column) is not None }
    df.rename(columns= renamedColumns, inplace= True)

    # TODO: rename dbA, dbT to dBA, dBT for consistencty
    # TODO: potentially drop siteID column

    # Coerce numeric columns to floats, in case of "-Infinity" values
    try:
        numericCols = [
            '12.5', '15.8', '20', '25', '31.5', '40', '50', '63', '80', '100',
            '125', '160', '200', '250', '315', '400', '500', '630', '800', '1000',
            '1250', '1600', '2000', '2500', '3150', '4000', '5000', '6300', '8000',
            '10000', '12500', '16000', '20000', 'dbA', 'dbC', 'dbF',
            'Voltage','WindSpeed', 'WindDir', 'TempIns', 'TempOut', 'Humidity'
         ]
        presentNumericCols = df.columns.intersection(numericCols)
        if len(presentNumericCols) > 0:
            # df[presentNumericCols] = df[presentNumericCols].convert_objects(convert_dates= False, convert_numeric= True, convert_timedeltas= False, copy= False)
            df[presentNumericCols].astype('float32', copy= False, raise_on_error= False)

    except KeyError:
        pass

    return df

@nvspl.initialize
def initializeNVSPL(endpoint, endpointParams, timestamps= None, columns= None):

    if timestamps is not None:
        # make dict of endpoint restriction args
        # make dict of argtuple: list of secs to read
        pass

    index_index = 1 # Default position of the index column (STime)
    if columns is not None:
        # Ensure we read the STime (date) column, otherwise indexing will be messed up
        # TODO: conversion between reasonable column names and 12p5h style names
        if all(isinstance(column, basestring) for column in columns):
            if "STime" not in columns:
                columns = ["STime"] + columns
            index_index = 0
        elif all(isinstance(column, int) for column in columns):
            if 1 not in columns:
                columns = [1] + columns
                columns.sort()
            index_index = columns.index(1)
        else:
            raise TypeError("columns must be a list of strings or of integers")

    return (timestamps, columns, index_index)



# def nvspl(ds, unit= None, site= None, year= None, month= None, day= None, hour= None, timestamps= None, columns= None):
#     # TODO:
#     # - Error handling, progress bar context manager? (Potentially shared with @accessor)
#     # - Handle Dataset, Endpoint, or iterable of str paths (i.e. Subset)
#     # - Advanced timestamp specification

#     # - Reasonable column name specification
#     # - Update numeric conversion to new pandas?
#     # - Make it fast.


#     if timestamps is not None:
#         # make dict of endpoint restriction args
#         # make dict of argtuple: list of secs to read
#         pass

#     index_index = 1 # Default position of the index column (STime)
#     columns = columns
#     if columns is not None:
#         # Ensure we read the STime (date) column, otherwise indexing will be messed up
#         # TODO: conversion between reasonable column names and 12p5h style names
#         types = list(map(type, columns))
#         if types == [str]*len(columns):
#             if "STime" not in columns:
#                 columns = ["STime"] + columns
#             index_index = 0
#         elif types == [int]*len(columns):
#             if 1 not in columns:
#                 columns = [1] + columns
#                 columns.sort()
#             index_index = columns.index(1)
#         else:
#             raise TypeError("onlyColumns must be a list of strings or of integers")

#     def generate():
#         entries = ds.nvspl(unit= unit, site= site, year= year, month= month, day= day, hour= hour)
#         for nvsplFileEntry in entries:
#             # try:
#             # if secsByFile:
#             #     rows = secsByFile[(nvsplFileEntry.unit, nvsplFileEntry.site, nvsplFileEntry.year, nvsplFileEntry.month, nvsplFileEntry.day, nvsplFileEntry.hour)]
            
#             df = pd.read_csv(str(nvsplFileEntry),
#                              engine= 'c',
#                              # sep= ',',
#                              parse_dates= True,
#                              index_col= index_index,
#                              infer_datetime_format= True,
#                              usecols= columns
#                              )

#             # Make column names slightly nicer
#             df.index.name = "date"
#             renamedColumns = { column: column.replace('H', '').replace('p', '.') for column in df.columns if re.match(r"H\d+p?\d*", column) is not None }
#             df.rename(columns= renamedColumns, inplace= True)

#             # TODO: rename dbA, dbT to dBA, dBT for consistencty
#             # TODO: potentially drop siteID column

#             # Coerce numeric columns to floats, in case of "-Infinity" values
#             try:
#                 numericCols = [
#                     '12.5', '15.8', '20', '25', '31.5', '40', '50', '63', '80', '100',
#                     '125', '160', '200', '250', '315', '400', '500', '630', '800', '1000',
#                     '1250', '1600', '2000', '2500', '3150', '4000', '5000', '6300', '8000',
#                     '10000', '12500', '16000', '20000', 'dbA', 'dbC', 'dbF',
#                     'Voltage','WindSpeed', 'WindDir', 'TempIns', 'TempOut', 'Humidity'
#                  ]
#                 presentNumericCols = df.columns.intersection(numericCols)
#                 if len(presentNumericCols) > 0:
#                     # df[presentNumericCols] = df[presentNumericCols].convert_objects(convert_dates= False, convert_numeric= True, convert_timedeltas= False, copy= False)
#                     df[presentNumericCols].astype('float32', copy= False, raise_on_error= False)

#             except KeyError:
#                 pass

#             nvsplFileEntry.data = df
#             yield nvsplFileEntry
#             # except:
#                 # print( traceback.format_exc() )

#     return Result(generate)

@accessor("srcid")
def srcid(entry):
    """
    Read a SPLAT SRCID file into a pandas DataFrame.

    The ``nvsplDate``, ``hr``, and ``secs`` columns are combined into a single DatetimeIndex for the DataFrame and dropped.
    The ``len`` column (length of the noise event) is converted to a pandas Timedelta.

    Returns
    -------
    DataFrame
    """

    with open(str(entry)) as f:
        # Determine version; older versions immediately start with header, newer has version comment
        firstline = f.readline()
        if not firstline.startswith(r"%%"):
            f.seek(0)   # Rewind, as we just consumed the header row.
                        # Otherwise, we consumed the comment row, which is fine

        data = pd.read_csv(f,
                            engine= "c",
                            sep= "\t",
                            # skiprows= 1,
                            parse_dates= False)

    # Combine nvsplDate, hr, secs columns into one DatetimeIndex
    dates = pd.to_datetime(data.nvsplDate, infer_datetime_format= True)
    hrs   = pd.to_timedelta(data.hr, unit= "h")
    secs  = pd.to_timedelta(data.secs, unit= "s")

    data.drop(["nvsplDate", "hr", "secs"], axis= 1, inplace= True)
    data.index = dates + hrs + secs

    # Turn len into timedelta
    data.len = pd.to_timedelta(data.len, unit= "s")

    if 'sID' in data.columns:
        # Some bizzare old files have a different name for srcID (really only DENAUSLC2008 so far)
        data.rename(columns= {'sID': 'srcID'}, inplace= True)

    # Days with no noise events are entered with the `MaxSPLt` and `SELt` columns skipped,
    # so they get filled with userName and tagDate, giving them a mixed type instead of float
    # Resolve this by finding zero-noise rows and setting all their values to NaN (more appropriate than 0)
    if 'MaxSPLt' in data.columns:
        if data.MaxSPLt.dtype == np.object:
            # There are noise-free days in this dataset
            converted = data[['MaxSPLt', 'SELt']].convert_objects(convert_numeric= True)
            noisefree = converted.isnull().all(axis= 1)
            data.loc[noisefree, ["userName", "tagDate"]] = data.loc[noisefree, ['MaxSPLt', 'SELt']].values
            data[['MaxSPLt', 'SELt']] = converted

            nanCols = data.columns.difference(("userName", "tagDate"))
            data.loc[ noisefree, nanCols ] = np.nan
    
    # Parse tagDate to datetime (though old versions don't have tagDate)
    if 'tagDate' in data.columns:
        data.tagDate = pd.to_datetime(data.tagDate, infer_datetime_format= True)

    return data