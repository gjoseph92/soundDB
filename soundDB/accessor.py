# Python 2 and 3 cross-compatibility:
from __future__ import print_function, division, unicode_literals, absolute_import
from builtins import (bytes, str, int, dict, object, range, map, filter, zip, round, pow, open)
from future.utils import (iteritems, itervalues)
from past.builtins import basestring

import itertools
import operator
import traceback
import collections
import inspect

import pandas as pd
import re

# MUST DO:
# [ ] Docs, duh
# [ ] 2-3 cross-compatibility
# [x] (Where) should iterators be consumed
# [x] Where to sort, if to sort
# [x] Better default ID for .all

# NICE EVENTUALLY:
# [ ] Accessor instances have own docstrings: parser docstring plus columns and dtypes of resulting data
# [ ] Helpful reprs
# [ ] Progressbar
# [ ] Auto-parallelization? (or kwarg for @accessor at least)
# [x] Specifying list of sites (as iterable of dicts/tuples, pandas index, etc) -- here and/or iyore
# [ ] Specifying list of filepaths/directories *without* iyore
# [ ] Combining datasets/endpoints -- here and/or iyore
# [-] Smart .all that promotes to next-dimensional structure  ==> may not actually be possible: Panel doesn't make sense for any data, as the minor axes (rows) aren't the same for all deployments, since they're timestamps
# [-] Should GroupbyApplier self-mutate? ==> keeping same model for now, generator comprehesion given to GroupbyApplier is still single-use, plus Pandas is also single-use

class GroupbyApplier:
    # given iter of (key, pandas.NDFrame)
    # all chained attribute access, item access, and method calls are applied to each NDFrame
    # calling compute() at end of chain combines the results into a dataframe indexed by key of the iter

    def __init__(self, iterator):
        # TODO: pass in name(s) by which data is grouped, to set df.index.name in compute() for niceness
        self._chain = []
        self._iter = iterator

    def compute(self):
        # TODO: should compute take an optional final function which is given the whole data to process?
        #       i.e. could be a function for computing bioacoustic metric from a whole DataFrame of NVSPL, etc
        # TODO: does this work on Metrics?
        results = {key: data for key, data in iter(self)}
        try:
            # TODO: this is horribly stupid and should actually be checked
            # TODO: if all data is DataFrame -> return Panel (well, only if columns & index are same for all),
            # if all Series -> return DataFrame, if all scaler, return Series
            return pd.DataFrame.from_dict(results, orient= "index")
        except ValueError:
            return pd.Series(results)

    def __iter__(self):
        for key, data in iter(self._iter):
            result = data
            for step in self._chain:
                if isinstance(step, basestring):
                    result = getattr(result, step)
                elif isinstance(step, tuple):
                    result = result(*step)
                elif isinstance(step, list):
                    result = result.__getitem__(*step)
            # print(key, result)
            yield key, result

    def __getattr__(self, attr):
        self._chain.append(attr)
        return self

    def __getitem__(self, *index):
        self._chain.append(list(index))
        return self

    def __call__(self, *args):
        self._chain.append(tuple(args))
        return self

    def __repr__(self):
        return repr(self._chain)


class Query(object):
    """
    A structure for holding a selection of data to access, and methods for reading it.

    Imagine the accessor functions are like custom machine shops. You specify exactly what kind of data you want
    (NVSPL, SRCID, etc.) and where you want it from (which Dataset, and any parameters restricting the year, site, etc.),
    and rather than just giving you the data, they build a custom machine for you that will go out and get exactly that data,
    whenever you tell it to. That machine is a Query.

    Why the extra step? Well, depending on how you plan to use the data, there are a few different ways to go about getting it,
    and making the right choice can make your program vastly more efficient.

    There are four primary ways to access data from a Query:

    - As an iterable, which yields Entry objects whose ``data`` attributes contain pandas structures.
      
          This is best for operations you want to perform one file at a time that can't be done with a pandas one-liner,
          like plotting. Iterating has the least memory overhead, since data is only kept from one file at a time.

    - ``.sorted()``: iterate in a particular order through Entry objects whose ``data`` attributes contain pandas structures.
      
          If you have a Query ``q``, ``for entry in q.sorted(lambda entry: entry.year)`` is significantly more memory-efficient
          than ``for entry in sorted(q, key= lambda entry: entry.year)``, since the latter reads and stores data from every file
          before sorting, while the former lets you only hold data from one file at a time in memory.

    - ``.groupby()``: bundle the data into groups by year, site, etc., apply operations to summarize each group,
      combine the results computed from all the groups into a DataFrame (like pandas groupby).

          ``.groupby()`` automatically optimizes memory useage: data is only stored in memory for one group at a time,
          then summary operations are computed and the raw data is discarded before reading the next group.
          This makes ``.groupby()`` the most powerful and most frequently used of these four methods.
   
    - ``.all()``: return a DataFrame of all the data contained in the Dataset.

          Though convenient for exploring small Datasets, computation using ``.all()`` can usually be done
          using ``.groupby()`` in some way, which will be much more efficient.
   
    - ``.one()``: return one Entry object whose ``data`` attribute contains a pandas structure

          A convenience method which is helpful for prototyping and exploration.

    See the documentation of each of these methods for specifics.
    """
    def __init__(self, endpoint, endpointFilters, parserFunc, prepareState= None, prepareStateParams= None):
        """
        Instantiate a query. There's no reason you should need to do this yourself.

        Parameters
        ----------

        endpoint : iyore.Endpoint

            The `iyore.Endpoint` from which to access data

        endpointFilters : dict

            Dict of keyword arguments to give to that Endpoint as filter parameters

        parserFunc : function

            The function to call on every Entry yielded from the Endpoint. Its signature must match:

            def parserFunc(entry: iyore.Entry, [state= default]) -> pandas.NDFrame
                 Parse a single file of a specific type in to a pandas structure
            
                 Parameters
                 ----------
                 entry : iyore.Entry
                     An entry for a single file.
                     If possible, parsers should not access any attributes from the Entry, and get its path using
                     ``str(entry)`` rather than ``entry.path``, so that the function can also be used with just
                     a string of the path to a file to read.
                 state : client-determined keyword argument, optional
                     An optional object, created in the initialization function,
                     which is passed into the parser function on every call for a Query.
                     (Often a dict or tuple.) This can be used to pass state between files read.
                     Though the object is created in ``prepareState``, it's safe for ``parserFunc``
                     to mutate.

        Keyword Args
        ------------

        prepareState : function, default None

            A function to create the initial ``params`` object which will be passed into the parserFunc each time it's called.
            Its signature must match:

            def prepareState(endpoint:iyore.Endpoint, endpointFilters: dict, [kwargs...]) -> object
                 Return the ``params`` object which will be passed into ``parserFunc`` on every call for this Query.
                 The params object can be any type (though dict usually makes most sense)
                 ``prepareState`` is called once, before each time the Query is used.
                 When the Query is used (by .all(), .groupby(), etc), any keyword arguments it's given
                 that match the keyword arguments taken by ``prepareState`` will be given to ``prepareState``.
                 Any remaining keyword arguments that do not share the same names are assumed to be parameters to
                 filter the Endpoint. The Endpoint instance, and a dict of these endpoint parameters, are given to
                 ``prepareState`` as its first two arguments, in case they're useful.

        prepareStateParams : dict, default None

            Dict of keyword arguments to give to prepareState

        """
        self.endpoint = endpoint
        self.endpointFilters = endpointFilters
        self.parserFunc = parserFunc
        self.prepareState = prepareState
        self.prepareStateParams = prepareStateParams

    def sorted(self, key):
        """
        Iterate through the data, with Entries sorted by the given key function

        Parameters
        ----------

        key : str, iterable of str, function

            If ``str`` or iterable of ``str``, should be field(s) of the given Endpoint.
            If a function, it should take an ``iyore.Entry`` and return a value to be used to determine its sort order,
            i.e. to sort by year, use ``lambda entry: entry.year``

        Yields
        ------
            `iyore.Entry` objects whose ``data`` attributes contain pandas structures
        """
        # TODO: any use case (/ is it possible) to define an explicit ordering rather than a key function?
        # TODO: allow client-facing keys, i.e. *args of strs?
        params = self.prepareState(self.endpoint, self.endpointFilters, **self.prepareStateParams) if self.prepareState is not None else None
        def iterate():
            for entry in self.endpoint(sort= key, **self.endpointFilters):
                try:
                    # time and parallelize if appropriate
                    entry.data = self.parserFunc(entry, params= params) if params is not None else self.parserFunc(entry)
                    yield entry
                except GeneratorExit:
                    raise GeneratorExit
                except:
                    print('Error while processing "{}":'.format(entry.path))
                    print( traceback.format_exc() )
        return iterate()

    def __iter__(self):
        """
        Iterate through the data in unspecified order.

        Yields
        ------
            `iyore.Entry` objects whose ``data`` attributes contain pandas structures
        """
        return self.sorted(None)

    def one(self):
        """
        Return one `iyore.Entry` object whose ``data`` attribute contains a pandas structure
        """
        return next(iter(self))

    def all(self, ID= None):
        """
        Return a pandas DataFrame of all the data contained in the Dataset.

        ``ID`` should be a function which, given an Entry, returns a unique string identifying
        which soundstation *deployment* it was from. The default is to concatenate the unit, site, and year fields.

        The resulting DataFrame will be hierarchically indexed, with the deployment ID at the outermost level.

        If the data in each Entry isn't a pandas structure (i.e. Metrics files), then a dict mapping
        deployment ID to a singleton or list of data objects for that ID is returned.
        """

        if ID is None:
            def defaultID(entry):
                """
                Given an Entry, return a string of whichever of the the fields "unit", "site", and "year"
                are available, concatenated together
                """
                id_elems = []
                if "unit" in entry.fields: id_elems.append(entry.unit)
                if "site" in entry.fields: id_elems.append(entry.site)
                if "year" in entry.fields: id_elems.append(entry.year)
                if len(id_elems) > 0:
                    return "".join(id_elems)
                else:
                    return entry.path
            ID = defaultID            

        # TODO?: any use case for a predicate/filter for which entries are included in all()? could be used for head() functionality?
        # TODO: ID= None to disable hierarchical indexing
        results = collections.defaultdict(list)
        # build map of {ID: [data, data, ...]} (same ID may have multiple data, i.e. NVSPL or LA)
        for e in iter(self):
            results[ID(e)].append(e.data)

        # flatten data for each ID by concatenating, or unpacking list if just one dataframe
        try:
            for ID_name, datas in iteritems(results):
                results[ID_name] = pd.concat(datas, copy= False) if len(datas) > 1 else datas[0]
        except TypeError:
            pass

        try:
            joined = pd.concat(results, copy= False)
            try:
                joined.index.set_names("ID", level= 0, inplace= True)
            except AttributeError:
                pass
            return joined
        except TypeError:
            return results

    def groupby(self, *groups):
        """
        Bundle the data into groups, apply operations to summarize each group,
        optionally combine the results computed from all the groups into a DataFrame.

        Groupby imitates the idea and syntax of pandas groupby, but optimizes memory use
        by only reading data from one group at a time.

        A groupby statement might look like this:
        ```
        >>> q = soundDB.nvspl(ds)
        >>> monthly_medians_df = q.groupby("site", "month").dbA.median().compute()
        #                                  |-- groups ---| |-- chain --|    \\________________
        #                                       /                |                            \\
        #                    (how to divide up data) (what to do to each group) (combine results into DataFrame/Series)
        ```
        
        Groups
        ------

        The argument(s) to .groupby() specify how to determine the groups into which data
        is bundled and computed.

        - If one or more strings, they refer to fields of the Endpoint
        (such as "unit", "site", "year", etc.).
        - If a function, it should take an Entry object (which has attributes for
        each field of the Endpoint) and return a string, tuple, number, or other
        immutable value identifying which group the Entry belongs to.

        All files which are members of the same group are read in together,
        and if there is more than one file in a group, the data from all files is
        concatenated into a single DataFrame.

        Note that no data is read from the files in the grouping phase, just their filenames.
        So data can only be grouped by metadata which can be gleaned from the text of the path
        to the file, not by their contents.

        Operations Chain
        ----------------

        Any method calls, attribute accesses, and item accesses ([] syntax) chained together
        (using ``.`` notation) after the call to ``.groupby()`` will be applied to the DataFrame
        of each group. This is similar to the way methods can be chained onto a pandas groupby operation,
        but with Query.groupby(), *any* chain of operations which could be applied to a single
        DataFrame can be used.

        In other words, these snippts are equivalent:
        ```
        for group, result in in q.groupby("site", "month").dBA.median():
            # use result (a single float of the median of the dBA column) somehow
        ```
        and
        ```
        for group, data in q.groupby("site", "month"):
            result = data.dbA.median()
            # use result (a single float of the median of the dBA column) somehow
        ```

        .compute()
        ----------
        Without ``.compute()``, the operations chain itself acts as an iterator yielding a tuple of
        ``(group, data)``, where ``data`` is the result of applying all the operations in the chain
        to the DataFrame of that group. (In most use cases, ``data`` is a single number or a pandas structure.)

        Adding ``.compute()`` to the end of the operations chain will combine the results from
        all groups into a single DataFrame or Series, indexed by group.

        ``.compute()`` makes it syntactically simple to efficiently calculate basic metrics and summaries
        on a site-by-site (or year-by-year, or any other) basis across large datasets in a single line of code.

        For example, 




        q.groupby("site", "month").loc[:, "200":"5000"].apply(some_function).compute()
        #         |-- groups ---|  |---------------- chain ----------------|

        ``q.groupby("month").MaxSPL.median().compute()`` uses significantly less memory than the equivalent
        ``q.all().groupby("month").MaxSPL.median()``. Note, however, that ``.groupby()`` can only group on fields
        in the Endpoint, i.e. only on metadata which can be gleaned from the text of the path to the file. So if you
        need to group by some columns of the data itself, you must use pandas groupby. Still, it's quite possible
        you'd want to do this data-grouping operation for every site, or year, or such, so you can combine ``Query.groupby()``
        with a pandas groupby in the operations chain to somewhat reduce memory useage:
        ``q.groupby("unit", "site").groupby("srcID").MaxSPL.median().compute()`` will require much less memory than
        ``q.all().groupby("srcID", level= "ID").MaxSPL.median()``.
        """

        # endpoint field name(s) str, or function
        if len(groups) == 0:
            raise TypeError("No groups given to groupby")
        elif len(groups) > 1:
            if all(isinstance(group, basestring) for group in groups):
                groupFunc = lambda e: tuple(getattr(e, group) for group in groups)
            else:
                raise TypeError("If multiple groups are given, all must be strings")
        else:
            group = groups[0]
            if isinstance(group, basestring):
                groupFunc = operator.attrgetter(group)
            else:
                if hasattr(group, "__call__"):
                    groupFunc = group
                else:
                    raise ValueError('Argument to groupby must be a string or function, instead got "{}"'.format(type(group)))

        # create ProgressBar

        def concat_maybe(datas):
            # for data in datas, append to list and update ProgressBar
            datas = tuple(datas)
            if len(datas) == 1:
                return datas[0]
            else:
                # TODO: try/except? (for metrics)
                return pd.concat(datas)

        sortedIterator = self.sorted(groupFunc)
        # ...but somehow have to figure out total number of files...
        groupedIterator = ( (key, concat_maybe(e.data for e in subiter)) for key, subiter in itertools.groupby(sortedIterator, groupFunc))
        return GroupbyApplier(groupedIterator) # maybe pass in Progressbar


class Accessor(object):
    """
    Base class to create classes for accessing a specific kind of data from an iyore Dataset.

    By subclassing Accessor and implementing a ``parse`` function, which holds the logic for
    reading a single file of a specific type into a pandas structure, Accessor provides the
    logic to vectorize that function so it can parse all instances of that data file from an Endpoint.
    """

    # Overridden in each subclass: name of the ``iyore.Endpoint`` where the kind of data
    # the Accessor handles is found
    endpointName = None

    def parse(entry, state= None):
        """
        Parse a single file of a specific type into a pandas structure.

        This method should be overridden in each subclass to actually read the type of file it handles.

        Parameters
        ----------
        entry : iyore.Entry
            An entry for a single file.
            If possible, parsers should not access any attributes from the Entry, and get its path using
            ``str(entry)`` rather than ``entry.path``, so that the function can also be used with just
            a string of the path to a file to read.
        state : client-determined keyword argument, optional
            An optional object, created in the initialization function,
            which is passed into the parser function on every call for a Query.
            (Often a dict or tuple.) This can be used to pass state between files read.
            Though the object is created in ``prepareState``, it's safe for ``parserFunc``
            to mutate.
        """
        raise NotImplementedError

    def prepareState(endpoint, endpointParams, **kwargs):
        """
        Optionally overridden in subclasses which need to pass state between multiple calls of
        ``parse()`` for the same Query

        Should return the ``state`` object which will be passed into ``parse`` on every call for a Query.
        The state object can be any type (though dict usually makes most sense).
        ``prepareState`` is called once, before each time the Query is used.

        When the Query is used (by .all(), .groupby(), etc), any keyword arguments it's given
        that match the keyword arguments taken by ``prepareState`` will be given to ``prepareState``.
        Any remaining keyword arguments that do not share the same names are assumed to be filters for the Endpoint.
        The Endpoint instance, and a dict of these endpoint parameters, are given to
        ``prepareState`` as its first two arguments, in case they're useful.
        """
        pass

    def __call__(self, ds, items= None, **filters):
        """
        Returns a Query to access data from the dataset ``ds`` which matches the given filters
        """
        try:
            endpoint = getattr(ds, self.endpointName)
        except AttributeError:
            raise ValueError('No endpoint "{}" exists in the given dataset'.format(self.endpointName))

        if items is not None:
            # TODO: selection based on parsing ID strings from DataFrame index, not just columns
            if isinstance(items, pd.DataFrame):
                paramColumns = items.columns.intersection(endpoint.fields)
                # TODO: may need to map a function which converts numerics to strings
                items = paramColumns.iterrows()

            filters["items"] = items

        # split prepareState params from endpoint filters
        if self.prepareState is not None:
            prepareStateParams = { kwarg: filters.pop(kwarg) for kwarg in self.prepareStateKwargs if kwarg in filters }
            return Query(endpoint, filters, self.parse, prepareState= self.prepareState, prepareStateParams= prepareStateParams)
        else:
            return Query(endpoint, params, self.parse)


    def __init__(self):
        if self.endpointName is None:
            raise NotImplementedError('No Endpoint name set for the Accessor "{}"'.format(self.__class__.__name__))

        # if prepareState is not overridden by subclass, eliminate it
        if self.prepareState.__func__ is Accessor.prepareState:
            self.prepareState = None
        else:
            # otherwise, find out what its keyword arguments are so they can be pulled out when the Accessor is called
            argspec = inspect.getargspec(self.prepareState)
            self.prepareStateKwargs = argspec.args[ -len(argspec.defaults): ]
            if "items" in self.prepareStateKwargs:
                raise TypeError("The keyword argument 'items' is already used by Accessor, please pick a different name")
