"""
This file holds specs that are in the new core3 archives but that don't have an entry
in the meta_data directory. This happens when the client itself collects the data
and puts it into the archive.
"""

from functools import partial

from insights.core.context import SerializedArchiveContext
from insights.core.spec_factory import simple_file
from insights.specs import Specs

simple_file = partial(simple_file, context=SerializedArchiveContext)


class Core3Specs(Specs):
    pass
