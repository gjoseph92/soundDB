# soundDB

A library for the [NPS Natural Sounds & Night Skies Division](https://www.nps.gov/orgs/1050/index.htm) to make going from data-somewhere-on-disk to data-ready-for-processing as painless as possible.

:construction: *README under construction. Proceed with care.* :construction:

----------------------------------

## Demo

```python
>>> import pandas as pd
>>> import iyore
>>> import soundDB

>>> ds = iyore.Dataset("E:/AKRO Soundscape Data/")
>>> ds
Dataset("E:/AKRO Soundscape Data/")
Endpoints:
  * audibility - fields: day, listener, month, name, site, unit, year
  * audio - fields: day, hour, min, month, name, sec, site, unit, year
  * dailypa - fields: name, site, unit, year
  * dataDir - fields: name, site, unit, year
  * dayAudibility - fields: day, listen_day, listen_month, listen_year, month, name, site, unit, year
  * loudevents - fields: name, site, unit, year
  * metrics - fields: name, site, unit, year
  * microarray - fields: name, site, unit, year
  * microarrayFiles - fields: ext, filename, name, site, unit, year
  * nvspl - fields: day, hour, month, name, site, unit, year
  * png - fields: day, month, name, site, unit, year
  * srcid - fields: name, site, unit, year
  * wav - fields: name, site, unit, year

# TODO: run these on acutal data

    # compute median event length by year, for years after 2008
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
2009    00:03:15
2010    00:03:20
2011    00:05:04
2012    00:04:22
2013    00:03:11
2014    00:05:01
2015    00:04:41
2016    00:04:16
dtype: timedelta64[ns]

    # compute median number of events above L_nat per hour for each year
>>> soundDB.loudevents(ds).group("year")["above"].median(axis=0).combine()
      2005  2006  2007  2008  2009  2010  2011  2012  2013  2014  2015  2016
hour                                                                        
0        1     3     0     3     4     4     3     2     4     0     5     5
1        1     2     4     3     4     4     1     3     2     2     5     5
2        4     2     3     0     5     3     2     4     5     0     2     4
3        4     2     2     1     2     5     5     2     3     5     5     1
4        5     4     0     1     5     1     2     3     3     2     3     3
5        0     0     1     4     1     1     1     0     5     1     0     2
6        0     5     0     0     0     3     2     5     5     5     4     3
7        1     3     3     1     1     0     2     2     5     4     0     3
8        5     3     0     1     5     2     4     1     5     1     4     4
9        4     2     5     5     2     0     1     5     5     5     1     2
10       4     5     5     2     1     4     4     1     5     0     0     5
11       5     2     2     4     4     5     5     3     2     2     2     4
12       5     3     0     1     0     4     1     0     2     0     0     1
13       1     1     5     2     4     3     0     1     4     1     4     3
14       2     1     5     1     2     3     5     0     4     3     1     0
15       5     5     0     4     0     5     4     5     5     5     0     5
16       2     3     4     0     0     1     5     0     4     5     4     1
17       4     2     1     0     1     0     2     4     3     1     5     1
18       5     0     3     4     0     1     0     1     5     3     2     0
19       5     5     4     3     5     4     0     0     1     4     3     3
20       2     4     0     2     2     2     0     3     4     4     5     2
21       5     3     1     1     4     2     0     4     0     3     2     0
22       0     5     2     1     3     1     2     1     3     3     0     1
23       1     3     3     5     1     0     4     0     0     2     3     1

    # read all listening center files for the sites THRI, UPST, and MURI
    # into a single pandas DataFrame
>>> df = soundDB.audibility(ds, site=["THRI", "UPST", "MURI"]).combine()

```

## First, the problem

These are the annoyances soundDB hopes to solve:

1. We have lots of natural sounds data (NVSPL files, audio, etc.), stored in lots of different places. Though the contents of the files is usually consistent, the way they're *organized* in all those different places often isn't. Code that reads all the NVSPL files for one park may not work for another, because they keep their NVSPL in a different place.
2. Many people have written functions for parsing the data. Many times. If we share one set of good parsing functions, we won't have to write them again.

Ask your doctor: if your data is always well-organized and you like rewriting code, soundDB may not be right for you.

## The system

soundDB solves problem 1 using the library [`iyore`](https://github.com/nationalparkservice/iyore). You should first read about iyore, since it's critical for using soundDB effectively. But here's the gist:

Your datasets may be organized in many different ways. But if you can tell iyore *how* each one is organized, then pulling out just the files you want is a snap. The names of the files, and the folders that contain them, convey valuable information. So with the knowledge of what those names mean, how they're formatted, and how they're nested, iyore lets you query your dataset for data which meets certain criteria, without ever opening the files themselves.

So iyore finds specific data files within a folder structure, then soundDB solves problem 2 with methods for reading those files into a useful format for further data processing in Python.

## How to use soundDB, piece by piece

Though just a single line, this code (which returns a pandas Series of the median noise event length for each year after 2008 in a dataset) ends up touching every important component of soundDB. It's also a good example of what a typical use of soundDB looks like.

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
```

Let's look at each part in detail, starting from the ground up:

### 1. iyore Datasets

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
#           ----- --  -----------------------------  -------------------------- --------
#      _______/    |                 |                           |                 |
#      |    #################        |                           |                 |
#      |    # iyore dataset #        |                           |                 |
#      |    #################        |                           |                 |
#      |                         filter(s)                       |                 |
#      |                                                         |                 |
#   Accessor method for data type                                |                 |
#                                                        operations chain    combine data
```

Your data might consist of many, many files, stored in many folders, all stored in one directory (or disk). That is your dataset. To make it an iyore Dataset (with a capital D), you need a **structure file** describing how the data is organized, and how to interpret the names of the files and folders.

A structure file is a plain-text file which describes the directory hierarchy of your dataset and where important data is found within it, denoting the patterns of the names of files and folders&mdash;and what parts of those names mean&mdash;using regular expressions.

To learn about structure file syntax, see the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#structuring).

Once you have a structure file written, save it in the root directory of your dataset (everything in a structure file is assumed to be relative to its location). The standard name is `.structure.txt`. Now your data is ready for iyore.

Say you have a dataset in the folder `AKRO Soundscape Data` on the E drive, and its structure file is named `.structure.txt`. Let's open it in iyore:

```python
>>> import iyore
>>> ds = iyore.Dataset("E:/AKRO Soundscape Data/")
```

`iyore.Dataset` takes the path to a dataset: either to a structure file, or to a directory which contains a structure file with the standard name `.structure.txt`.

```python
>>> ds
Dataset("E:/AKRO Soundscape Data/")
Endpoints:
  * audibility - fields: day, listener, month, name, site, unit, year
  * audio - fields: day, hour, min, month, name, sec, site, unit, year
  * dailypa - fields: name, site, unit, year
  * dataDir - fields: name, site, unit, year
  * dayAudibility - fields: day, listen_day, listen_month, listen_year, month, name, site, unit, year
  * loudevents - fields: name, site, unit, year
  * metrics - fields: name, site, unit, year
  * microarray - fields: name, site, unit, year
  * microarrayFiles - fields: ext, filename, name, site, unit, year
  * nvspl - fields: day, hour, month, name, site, unit, year
  * png - fields: day, month, name, site, unit, year
  * srcid - fields: name, site, unit, year
  * wav - fields: name, site, unit, year
```

You can see all the **Endpoints** this Dataset contains, such as `audio`, `nvspl`, `srcid`, etc. Endpoints are specified by the structure file, and refer to each of the specific kinds data available in the Dataset. They're used to filter and locate data within the Dataset.

Again, to learn about iyore Datasets and what they do, consult the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#iterating).

### 2. Filtering

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
#           ----- --  ------------------------------ -------------------------- ---------
#      _______/    |                 |                           |                 |
#      |      iyore dataset          |                           |                 |
#      |                       #############                     |                 |
#      |                       # filter(s) #                     |                 |
#      |                       #############                     |                 |
#   Accessor method for data type                                |                 |
#                                                       operations chain     combine data
```

The main thing iyore Datasets do is allow you to filter your data to find files that match certain criteria, which is explained in the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#filtering). (Hopefully it's clear by now that understanding iyore is a prerequisite to using soundDB.)

For example, to find NVSPL files from the park unit Denali, all site codes except `FANG` and `WEKH`, from the months of March, April, and May, and years after 2009:

```python
>>> for entry in ds.nvspl(unit= "DENA", site= {"FANG": False, "WEKH": False}, month= ["03","04","05"], year= lambda y: int(y) > 2009):
...     print(entry.fields)
...     print("  * "+entry.path)
...
{'month': '05', 'name': 'West Buttress', 'day': '28', 'hour': '00', 'unit': 'DENA', 'year': '2010', 'site': 'WEBU'}
"  * E:2010 DENAWEBU West Buttress\01 DATA\NVSPL\NVSPL_DENAWEBU_2010_05_28_00.txt"
{'month': '05', 'name': 'West Buttress', 'day': '28', 'hour': '01', 'unit': 'DENA', 'year': '2010', 'site': 'WEBU'}
"  * E:2010 DENAWEBU West Buttress\01 DATA\NVSPL\NVSPL_DENAWEBU_2010_05_28_01.txt"
{'month': '05', 'name': 'West Buttress', 'day': '28', 'hour': '02', 'unit': 'DENA', 'year': '2010', 'site': 'WEBU'}
"  * E:2010 DENAWEBU West Buttress\01 DATA\NVSPL\NVSPL_DENAWEBU_2010_05_28_02.txt"
# ...and so on
```

If you look back one section, notice that `unit`, `site`, `month`, and `year` are all listed as **fields** for the "nvspl" Endpoint of the Dataset. So to filter an Endpoint, you can use a keyword argument for each field you want to filter and a predicate for how to filter it. Predicates can be of many types, from strings to lists to functions, and each type has a different meaning. Of course, you already know this from the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#filtering).

This same filtering syntax is used when actually accessing data in your dataset, instead of just locating it with iyore:

### 3. Different Accessors, same interface

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
#           ----- --  ------------------------------ -------------------------- ---------
#      _______/    |                 |                           |                 |
#      |      iyore dataset          |                           |                 |
#      |                             |                           |                 |
#      |                         filter(s)                       |                 |
# #################################                              |                 |
# # Accessor method for data type #                              |                 |
# #################################                     operations chain     combine data
```

iyore finds the data you want. The soundDB Accessors then read it into a useful structure. soundDB has accessors for reading these kinds of data:

  Name in soundDB    |                           File type read
-------------------- | --------------------------------------------------------------------
`soundDB.nvspl`      | NVSPL files (i.e. `NVSPL_DENA7MIL_2001_12_29_00.txt`)
`soundDB.srcid`      | SRCID files from SPLAT (i.e. `SRCID_DENA7MIL.txt`)
`soundDB.loudevents` | LOUDEVENTS files (i.e. `LOUDEVENTS_DENA7MIL.txt`)
`soundDB.audibility` | Listening Center files (i.e. `LA_DENABACK_2014_04_16_gjoseph.txt`)
`soundDB.dailypa`    | Daily percent-time audible files (i.e. `DAILYPA_DENA7MIL.txt`)
`soundDB.metrics`    | Metrics files (i.e. `Metrics_DENA7MIL.txt`)

All of these Accessors work in the same way: given a Dataset (and possibly filters and other optional arguments), iterating through them yields tuples of `(key, data)`. `data` is usually a pandas data structure, but that varies between Accessors based on what's most appropriate for representing their data. `key` identifies where the data comes from&mdash;it's normally the iyore Entry from which the data was read; see below for when it's not. (Note on terminology: an Entry is a dict-like object of a single directory entry in a Dataset, and the information that can be parsed out of its name. We say "Entry" instead of "file", because it could refer to either a file or a directory, though file is most common.)

So the signature for an Accessor is:

```
Accessor(ds, n= None, items= None, sort= None, **filters) -> Iterator[Tuple[key, data]]
```

Notice that most of those arguments look the same as for an iyore Endpoint&mdash;because they are. The filter keyword arguments given to an Accessor, along with `items` and `sort`, are passed into the Endpoint that the Accessor reads its data from.

#### Parameters:

+ `ds`: *iyore.Dataset*

    The dataset to use. Each Accessor knows the name of the endpoint in which to find its data (i.e. the NVSPL Accessor will look for an "nvspl" endpoint in `ds`).

+ `n`: *int, default None*

    Maximum number of Entries to read; handy for prototyping on big Datasets

+ `items`: *List[dict], default None*

    If given, yields data which matches any of the filter dicts in the list.
    Equivalent to the `items` argument of an iyore.Endpoint, which of course is documented in [the README](https://github.com/nationalparkservice/iyore#accessing-specific-entries)

+ `sort`: *str, Sequence[Str], or Callable[iyore.Entry], default None*

    Order data by the given field name(s) or key function. Equivalent to the `sort` argument of an iyore.Endpoint, as documented in [the README](https://github.com/nationalparkservice/iyore#sorting)

+ `**filters`: *field_name=str, numeric, Iterable[str], Mapping[str, False], or Callable[[str], bool]*

    Keyword argument for each field to filter, and predicate for how to filter it. Equivalent to filters of an iyore.Endpoint. See the [filtering section](#2-filtering) and the [iyore README](https://github.com/nationalparkservice/iyore#filtering).

+ Other optional arguments:

    Specific Accessors can have additional arguments of their own. For example, `soundDB.nvspl` has the `columns` argument to specify which columns to read. See the built-in help for each Accessor for these.

### 4. Operating on data

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
#           ----- --  ------------------------------ -------------------------- ---------
#      _______/    |                 |                           |                 |
#      |      iyore dataset          |                           |                 |
#      |                             |                           |                 |
#      |                         filter(s)                       |                 |
#      |                                                         |                 |
#   Accessor method for data type                     ####################         |
#                                                     # operations chain #   combine data
#                                                     ####################
```

Accessors let you iterate through the data one-by-one. Often, you want to apply the same operation to each piece of data. To simplify that, you can chain methods onto an Accessor which it will apply to each piece of data it processes.

For example, `soundDB.srcid` yields pandas DataFrames which include the columns `len` and `MaxSPL`. To subselect just those two columns and compute their median for every SRCID file in the Dataset, you could do this:

```python
>>> for entry, data in soundDB.srcid(ds):
...   result = data[["len", "MaxSPL"]].median()
...   print(entry.site)
...   print(result)
...   print()
MURI
len       0 days 00:04:10
MaxSPL               49.9
dtype: object

WOCR
len       0 days 00:04:17
MaxSPL               39.9
dtype: object

# ..and so on
```

Or, more concisely, apply those operations directly onto the Accessor:

```python
>>> for entry, result in soundDB.srcid(ds)[["len", "MaxSPL"]].median():
...   print(entry.site)
...   print(result)
...   print()
MURI
len       0 days 00:04:10
MaxSPL               49.9
dtype: object

WOCR
len       0 days 00:04:17
MaxSPL               39.9
dtype: object

# ..and so on
```

In general, any combination of attribute access (`.` notation), indexing (`[]` syntax), and calling (`(arg1, ...)` syntax) you do to an Accessor will be applied to the `data` it yields. Together, this is called the **operations chain**.

```
Accessor -- yields --> Entry, data                      Entry, processed data
                                ⤷---- Operations Chain -------------------⤴
                   --> Entry, data                      Entry, processed data
                                ⤷---- Operations Chain -------------------⤴
                   --> Entry, data                      Entry, processed data
                                ⤷---- Operations Chain -------------------⤴
                   ...and so on
```

#### Grouping

```
Accessor.group(key) --> Entry, data --\
                    --> Entry, data ---| == combine data within group ==> group_key, data                  group_key, processed data
                    --> Entry, data --/                                               ⤷---- Operations Chain -------------------⤴
                    --> Entry, data --\
                    --> Entry, data ---| == combine data within group ==> group_key, data                  group_key, processed data
                    --> Entry, data --/                                               ⤷---- Operations Chain -------------------⤴
```

### 5. Combining results



- Setting up python & miniconda
- Knowledge prereqs: pandas, numpy, python basics


-------------------

## Installation

### Windows

If you are using conda on Windows, you need to ensure the difficult compiled libraries are installed the easy way, via conda:

1. Install numpy and pandas: `conda install numpy pandas`
2. Let pip install soundDB and iyore: `pip install --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB`
3. When you need to upgrade soundDB, ensure that pip doesn't try to upgrade numpy and pandas as well: `pip install --upgrade --no-deps --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ iyore soundDB`

### Everyone else

Just use this command to both install and upgrade:

```
pip install --upgrade --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB
```