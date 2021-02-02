"""
Satellite MongoDB Commands
==========================

Parsers included in this module are:

MongoDBStorageEngine - command ``mongo pulp_database --eval 'db.serverStatus().storageEngine'``
-----------------------------------------------------------------------------------------------
MongoDBNonYumTypeRepos - command ``mongo pulp_database --eval 'db.repo_importers.find({"importer_type_id": { $ne: "yum_importer"}}).count()'``
----------------------------------------------------------------------------------------------------------------------------------------------

"""
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.satellite_mongodb_storage_engine)
class MongoDBStorageEngine(CommandParser, dict):
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
        <class 'insights.parsers.satellite_mongodb.MongoDBStorageEngine'>
        >>> satellite_storage_engine['name']
        'wiredTiger'

    Raises::

        SkipException: When there is no attribute in the output
        ParseException: When the storage engine attributes aren't in expected format
    """

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
                    name, value = [i.strip(' ,"') for i in line.split(':', 1)]
                    self[name] = value
                except Exception:
                    raise ParseException("Unable to parse the line: {0}".format(line))
        if not self:
            raise SkipException("Cannot get storage engine from Satellite MongoDB")


@parser(Specs.satellite_non_yum_type_repos)
class MongoDBNonYumTypeRepos(CommandParser):
    """
    Read the ``mongo pulp_database --eval 'db.repo_importers.find({"importer_type_id": { $ne: "yum_importer"}}).count()'`` command
    and save the count to attribute named count.

    Sample Output::

        MongoDB shell version v3.4.9
        connecting to: mongodb://127.0.0.1:27017/pulp_database
        MongoDB server version: 3.4.9
        0

    Examples::

        >>> type(satellite_non_yum_type_repos)
        <class 'insights.parsers.satellite_mongodb.MongoDBNonYumTypeRepos'>
        >>> satellite_non_yum_type_repos.count
        0

    Attributes::

        count (int): The count of non-yum type repos in pulp_database

    Raises::

        SkipException: When the output isn't in exptected format
    """

    def parse_content(self, content):
        if len(content) != 4 or not content[3].isdigit():
            raise SkipException("Unexpected output for MongoDBNonYumTypeRepos")
        self.count = int(content[3])
