"""
SatelliteMongoDBStorageEngine - command ``mongo pulp_database --eval 'db.serverStatus().storageEngine'``
========================================================================================================

The satellite mongodb storage engine parser reads the output of
``mongo pulp_database --eval 'db.serverStatus().storageEngine'`` and
set the storage engine to atribute ``name``.

Sample output of ``mongo pulp_database --eval 'db.serverStatus().storageEngine'``::

    MongoDB shell version v3.4.9
    connecting to: mongodb://127.0.0.1:27017/pulp_database
    MongoDB server version: 3.4.9
    {
            "name" : "wiredTiger",
            "supportsCommittedReads" : true,
            "readOnly" : false,
            "persistent" : true
    }

Examples:

    >>> type(satellite_storage_engine)
    <class 'insights.parsers.satellite_mongodb_storage_engine.SatelliteMongoDBStorageEngine'>
    >>> satellite_storage_engine.name
    'wiredTiger'
"""

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.satellite_mongodb_storage_engine)
class SatelliteMongoDBStorageEngine(CommandParser):
    """
    Read the ``mongo pulp_database --eval 'db.serverStatus().storageEngine'`` command

    Attributes:
        name(str): the storage engine used by satellite pulp_database
    """

    def parse_content(self, content):
        self.name = ''
        for line in content:
            if line.strip().startswith('"name"'):
                self.name = line.split(':')[1].strip(',').strip().strip('"')
                break
        if not self.name:
            raise SkipException("can not get storage engine for satellite")
