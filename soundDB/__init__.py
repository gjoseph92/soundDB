from .accessor import Accessor
from . import parsers

import inspect

def populateAccessors():
    """
    Find all filetype-specific Accessor subclasses in the parsers file (i.e. NVSPL, SRCID, etc.) and instantiate them.
    This way, one instance of each Accessor is added to the soundDB namespace under the name of the Endpoint it uses.
    """

    predicate = lambda obj: inspect.isclass(obj) and issubclass(obj, Accessor) and obj is not Accessor
    specificAccessorSubclasses = inspect.getmembers(parsers, predicate)
    accessors = { cls.endpointName: cls for name, cls in specificAccessorSubclasses }

    return accessors

globals().update(populateAccessors())

del inspect, accessor, parsers, populateAccessors
