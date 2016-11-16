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
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).groupby("year").len.median().compute()
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
>>> soundDB.loudevents(ds).groupby("year")["above"].median(axis=0).compute()
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
>>> df = soundDB.audibility(ds, site=["THRI", "UPST", "MURI"]).all()

```

## First, the problem

These are the annoyances soundDB hopes to solve:

1. We have lots of natural sounds data (NVSPL files, audio, etc.), stored in lots of different places. Though the contents of the files is usually consistent, the way they're *organized* in all those different places often isn't. Code that reads all the NVSPL files for one park may not work for another, because they keep their NVSPL in a different place.
2. Many people have written functions for parsing the data. Many times. If we share one set of good parsing functions, we won't have to write them again.

Ask your doctor: if your data is always well-organized and you like rewriting code, soundDB may not be right for you.

## The system

soundDB solves problem 1 using the library [`iyore`](https://github.com/nationalparkservice/iyore). You should first read about iyore, since it's critical for using soundDB effectively. But here's the gist:

Your datasets may be organized in many different ways. But if you can tell iyore *how* each one is organized, then pulling out just the files you want is a snap. The names of the files, and the folders that contain them, convey valuable information. So with the knowledge of what those names mean and how they're formatted, iyore lets you query your dataset for data which meets certain criteria, without ever opening the files themselves.

So iyore finds specific data files within a folder structure, then soundDB solves problem 2 with methods for reading those files into a useful format for further data processing in Python.

## How to use soundDB, piece by piece

Though just a single line, this code (which returns a pandas Series of the median noise event length for each year after 2008 in a dataset) ends up touching every important component of soundDB. It's also a good example of what a typical use of soundDB looks like, and consists of.

```python
>>> soundDB.srcid(ds, year= lambda y: int(y) > 2008).groupby("year").len.median().compute()
#           ----- --  -----------------------------  --------------------------------------
#      _______/    |                 |                                |
#      |      iyore dataset          |                                |
#      |                             |                                |
#      |                         filter(s)                            |
#      |                                                              |
#   Accessor method for data type                                     |
#                                               Retrieving data from Query (using .groupby in this case)
```

Let's look at each of those parts in detail, starting from the ground up:

### 1. iyore Datasets

Your data might consist of many, many files, stored in many folders, all stored in one directory (or disk). That is your dataset. To make it an iyore Dataset (with a capital D), you need a **structure file** describing how the data is organized, and how to interpret the names of the files and folders.

A structure file is a plain-text file which describes the directory hierarchy of your dataset and where important data is found within it, denoting the patterns of the names of files and folders&mdash;and what parts of those names mean&mdash;using regular expressions.

To learn about structure file syntax, see the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#structuring).

Once you have a structure file written, save it in the root directory of your dataset (everything written in a structure file is assumed to be relative to its location). The standard name is `.structure.txt`. Now your data is ready for iyore.

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

Again, to learn about iyore Datasets and what they do, consult the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#iterating).

### 2. Filtering

The main thing iyore Datasets do is allow you to filter your data to find files that match certain criteria, which is explained in the [iyore README](https://github.com/nationalparkservice/iyore/blob/master/README.md#filtering). (Hopefully it's clear by now that understanding iyore is a prerequisite to using soundDB.)




### 3. Different Accessors, same interface

### 4. Using Queries



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