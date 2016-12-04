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

    # compute median event length by year, for years after 2008
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
100%|###########################################| 44/44 [00:00<00:00, 56.19entries/s]
2009   00:03:04
2010   00:03:51
2011   00:03:54
2012   00:01:01
dtype: timedelta64[ns]

    # compute median number of events above L_nat per hour for each year
>>> soundDB.loudevents(ds)["above"].group("year").median().combine()
100%|##########################################| 62/62 [00:00<00:00, 109.77entries/s]
      2001  2002  2005  2006  2007  2008  2009  2010  2011  2012
hour
0        0     0     0     0     0     0     0     0     0     0
1        0     0     0     0     0     0     0     0     0     0
2        0     0     0     0     0     0     0     0     0     0
3        0     0     0     0     0     0     0     0     0     0
4        0     0     0     0     0     0     0     0     0     0
5        0     0     0     0     0     0     0     0     0     0
6        0     0     0     0     0     0     0     0     0     0
7        0     0     0     0     0     0     0     0     0     0
8        0     1     1     1     0     0     0     0     0     0
9        1     2     1     1     0     0     0     0     0     0
10       1     4     1     1     1     0     0     1     1     0
11       2     5     2     1     0     1     1     1     1     0
12       2     5     1     1     1     0     1     1     1     0
13       2     5     1     2     0     0     0     0     0     0
14       2     5     1     1     0     0     0     0     0     0
15       4     4     1     1     0     1     0     0     1     0
16       2     4     2     1     1     0     0     0     0     0
17       2     5     1     1     0     0     0     0     1     0
18       1     4     1     1     0     0     0     0     1     0
19       1     4     1     1     0     0     0     0     0     0
20       0     3     1     1     0     0     0     0     0     0
21       0     1     0     0     0     0     0     0     0     0
22       0     0     0     0     0     0     0     0     0     0
23       0     0     0     0     0     0     0     0     0     0
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
...
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
...
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

In general, any combination of attribute access (`.` notation), indexing (`[]` syntax), and calling (`(arg1, ...)` syntax) you do to an Accessor will be applied to the `data` it yields. Together, this is called the **operations chain**. The flow looks like this:

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

You can add the `.group()` method into the operations chain to combine the data of related Entries together&mdash;the arguments to `.group()` specify which field(s) to group by. Any operations in the chain following `.group()` will be applied to the data of each group as a whole, rather than file-by-file.

For example, to compute the median `MaxSPL` value in all SRCID files for each year:

```python
>>> for key, data in soundDB.srcid(ds).group("year").MaxSPL.median():
...     print(data, "dB :", key)
...
50.2 dB : 2001
60.1 dB : 2002
45.2 dB : 2005
47.05 dB : 2006
# ...and so on
```

So the `srcid` Accessor first reads all data from the year 2001. If there is more than one SRCID Entry from 2001, all of that data is concatenated into a single pandas DataFrame. Then the rest of the operations chain (`.MaxSPL.median()`) is applied to that single concatenated DataFrame, and the iterator yields that result. Then this continues for 2002, and so on. This is particularly powerful since only one group's data needs to be held in memory at a time, so very large datasets which would not fit in memory can be easily processed group-by-group.

So using `.group()`, the flow looks like:

```
Accessor.group(key) --> Entry, data --\
                    --> Entry, data ---| == combine data within group ==> group_key, data                  group_key, processed data
                    --> Entry, data --/                                               ⤷---- Operations Chain -------------------⤴
                    --> Entry, data --\
                    --> Entry, data ---| == combine data within group ==> group_key, data                  group_key, processed data
                    --> Entry, data --/                                               ⤷---- Operations Chain -------------------⤴
```

The argument(s) to `.group()` can be:

- One or more strings which refer to fields of the Endpoint
(such as "unit", "site", "year", etc.).
- A function which takes an Entry object and returns a string, tuple, number, or other
immutable value identifying which group the Entry belongs to.

Note that no data is read from the files in the grouping phase, just their filenames.
So data can only be grouped by metadata which can be gleaned from the text of the path
to the file, not by their contents.

Remember that iterating through an Accessor yields a tuple of `(key, data)`? Without `.group()`, `key` is the Entry from which the data was read. With `.group()`, `key` becomes the group that data represents. (`key` will be a string, or a tuple of strings if you used multiple groups, or maybe something else if you used your own grouping function.)

Though `.group()` will most commonly come first in the operations chain, it doesn't have to. Any operations before `.group()` will be applied to the data from each Entry, and operations after are applied to the combined data for each group.

### 5. Combining results

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
#           ----- --  ------------------------------ -------------------------- ---------
#      _______/    |                 |                           |                 |
#      |      iyore dataset          |                           |                 |
#      |                             |                           |                 |
#      |                         filter(s)                       |                 |
#      |                                                         |                 |
#   Accessor method for data type                                |         ################
#                                                       operations chain   # combine data #
#                                                                          ################
```

All our examples so far have used a for loop to iterate through the Accessor:

```python
>>> for key, data in soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median():
...   print(key, ":", data)
...
2009 : 0 days 00:03:04
2010 : 0 days 00:03:51
2011 : 0 days 00:03:54
2012 : 0 days 00:01:01
```

That gets annoying.

Instead, tacking `.combine()` onto the end of the operations chain will, unsurprisingly, combine all of the results into a single data structure and return it:

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).group("year").len.median().combine()
100%|###################################################| 44/44 [00:00<00:00, 68.20entries/s]
2009   00:03:04
2010   00:03:51
2011   00:03:54
2012   00:01:01
dtype: timedelta64[ns]
# ^ this is a pandas Series
```

You even get a progress bar. How nice.

`.combine()` will feign a bit of intelligence by putting your data into whatever structure seems the most appropriate. Generally, this is the logic:

- If all the data have mostly the same axis values (i.e. same labels for rows/columns), the data will be *promoted* into the next-higher-dimensional data structure (i.e. scalars --> Series, Series --> DataFrame, DataFrames --> Panel)
- If index values differ (but columns are mostly the same, if a DataFrame), the data will be concatenated
- If all the axis values are wildly different, or the data aren't pandas structures, `.combine()` will throw up its hands, mutter about idiomatic data types, and return to you a dict of `{ID (a string): data}`.

`.combine()` also takes a keyword argument `func`, so you can pass the data through a final processing function. For each piece of data, `func` will be called with that data as its argument (and any other arguments given to `.combine()` are passed on to `func`), and its result is what will ultimately be combined. If working with pandas structures, it's better to use [`pipe()`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.pipe.html), but `func` is there if you need it.

### 6. Review

Let's summarize:

iyore Datasets allow data to be located based on patterns in the names of files and folders.

```python
>>> import iyore
>>> ds = iyore.Dataset("E:/AKRO Soundscape Data/")
>>> ds
Dataset("E:/AKRO Soundscape Data/")
Endpoints:
  * audibility - fields: day, listener, month, name, site, unit, year
  * audio - fields: day, hour, min, month, name, sec, site, unit, year
  * dailypa - fields: name, site, unit, year
  * loudevents - fields: name, site, unit, year
  * metrics - fields: name, site, unit, year
  * nvspl - fields: day, hour, month, name, site, unit, year
  * srcid - fields: name, site, unit, year
```

iyore just locates data, but doesn't read it.

```python
>>> for entry in ds.nvspl(unit= "DENA", year= ["2010", "2011"]):
...     print(entry.path)
... 

```

Accessors read the data that iyore locates. Given an iyore Dataset and keyword arguments for how to filter it, they act as iterators, yielding tuples of `(key, data)`.

```python
>>> for entry, data in soundDB.nvspl(ds, unit= "DENA", year= ["2010", "2011"]):
...     print(entry.path)
...     print(data)
... 
```

Any operations chained onto an Accessor will be applied to `data` on each iteration.

```python
>>> for entry, data in soundDB.nvspl(ds, unit= "DENA", year= ["2010", "2011"]).query("WindSpeed < 1").dbA.median():
...     print(entry.path)
...     print(data)
... 
```

Adding `.group()` into that operations chain (and specifying the fields to group by) will combine data within Entries of the same group, and subsequent operations in the chain are applied to each group's combined data.

```python
>>> for entry, data in soundDB.nvspl(ds, unit= "DENA", year= ["2010", "2011"]).group("site").query("WindSpeed < 1").dbA.median():
...     print(entry.path)
...     print(data)
... 
```

Suffixing the operations chain with `.combine()` will combine all the data into a single structure and return it.

```python
>>> soundDB.nvspl(ds, unit= "DENA", year= ["2010", "2011"]).group("site").query("WindSpeed < 1").dbA.median().combine()
```

-------------------

## Installation

### Windows

If you are using conda on Windows, you need to ensure the difficult compiled libraries are installed the easy way, via conda:

1. Install numpy and pandas: `conda install pandas=0.18.1 numpy`
  - soundDB is currently only compatible with pandas v0.18 (see issue #5)
2. Let pip install soundDB and iyore: `pip install --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB`
3. When you need to upgrade soundDB, ensure that pip doesn't try to upgrade numpy and pandas as well: `pip install --upgrade --no-deps --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ iyore soundDB`

### Everyone else

Just use this command to both install and upgrade:

```
pip install --upgrade --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB
```