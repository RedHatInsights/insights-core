"""
Satellite MongoDB Commands
==========================

Parsers included in this module are:

SatelliteMongoDBStorageEngine - command ``mongo pulp_database --eval 'db.serverStatus().storageEngine'``
--------------------------------------------------------------------------------------------------------
The satellite mongodb storage engine parser reads the output of
``mongo pulp_database --eval 'db.serverStatus().storageEngine'`` and
save the storage engine attributes to a dict.

"""
import re

from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.satellite_mongodb_storage_engine)
class SatelliteMongoDBStorageEngine(CommandParser, dict):
    """
    Read the ``mongo pulp_database --eval 'db.serverStatus().storageEngine'`` command
    and save the storage engine attributes to a dict.

    Sample Output::

        MongoDB shell version v3.4.9
        connecting to: mongodb://127.0.0.1:27017/pulp_database
        MongoDB server version: 3.4.9
        {
                "name" : "wiredTiger",
                "supportsCommittedReads" : true,
                "readOnly" : false,
                "persistent" : true
        }

    Examples::

        >>> type(satellite_storage_engine)
        <class 'insights.parsers.satellite_mongodb.SatelliteMongoDBStorageEngine'>
        >>> satellite_storage_engine['name']
        'wiredtiger'

    Raises::

        SkipException: When there is no attribute in the output
        ParseException: When the storage engine attributes aren't in expected format
    """

    def _remove_special_chars(self, str_name, special_chars):
        for char in special_chars:
            str_name = str_name.replace(char, '')
        return str_name

    def parse_content(self, content):
        start_parse = False
        for line in content:
            line = line.strip()
            if not start_parse and line == '{':
                start_parse = True
                continue
            if start_parse and line == '}':
                break
            if start_parse:
                try:
                    name, value = line.split(':', 1)
                    name = self._remove_special_chars(name, ' "')
                    value = self._remove_special_chars(value, ' ,"').lower()
                    if value in ("on", "yes", "true"):
                        value = True
                    if value in ("off", "no", "false"):
                        value = False
                    self[name] = value
                except Exception:
                    raise ParseException("Unable to parse the line: {}".format(line))
        if not self:
            raise SkipException("can not get storage engine for satellite")
