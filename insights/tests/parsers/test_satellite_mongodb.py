import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException
from insights.parsers import satellite_mongodb


MONGO_PULP_STORAGE_ENGINE_OUTPUT1 = '''
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
MongoDB server version: 3.4.9
{
        "name" : "wiredTiger",
        "supportsCommittedReads" : true,
        "readOnly" : false,
        "persistent" : true
}
'''


MONGO_PULP_STORAGE_ENGINE_OUTPUT2 = '''
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
MongoDB server version: 3.4.9
'''

MONGO_PULP_STORAGE_ENGINE_OUTPUT3 = '''
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
2020-02-13T23:19:57.750-0500 W NETWORK  [thread1] Failed to connect to 127.0.0.1:27017, in(checking socket for error after poll), reason: Connection refused
2020-02-13T23:19:57.751-0500 E QUERY    [thread1] Error: couldn't connect to server 127.0.0.1:27017, connection attempt failed :
connect@src/mongo/shell/mongo.js:237:13
@(connect):1:6
exception: connect failed
'''.strip()

MONGO_PULP_STORAGE_ENGINE_OUTPUT4 = '''
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
{
    "name" wrong data
}
'''.strip()

MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT1 = """
0
"""

MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT2 = """
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
MongoDB server version: 3.4.9
0
"""

MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT3 = """
MongoDB shell version v3.4.9
connecting to: mongodb://127.0.0.1:27017/pulp_database
MongoDB server version: 3.4.9
ab
"""


def test_doc_examples():
    engine_output = satellite_mongodb.MongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT1))
    repos_output = satellite_mongodb.MongoDBNonYumTypeRepos(context_wrap(MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT2))
    globs = {
        'satellite_storage_engine': engine_output,
        'satellite_non_yum_type_repos': repos_output
    }
    failed, tested = doctest.testmod(satellite_mongodb, globs=globs)
    assert failed == 0


def test_satellite():
    output = satellite_mongodb.MongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT1))
    assert output['supportsCommittedReads'] == 'true'
    assert output['readOnly'] == 'false'
    assert output['persistent'] == 'true'


def test_no_storage_engine():
    with pytest.raises(SkipException):
        satellite_mongodb.MongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT2))
    with pytest.raises(SkipException):
        satellite_mongodb.MongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT3))
    with pytest.raises(ParseException):
        satellite_mongodb.MongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT4))


def test_bad_yum_repos_output():
    with pytest.raises(SkipException):
        satellite_mongodb.MongoDBNonYumTypeRepos(context_wrap(MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT1))
    with pytest.raises(SkipException):
        satellite_mongodb.MongoDBNonYumTypeRepos(context_wrap(MONGO_PULP_NON_YUM_TYPE_REPOS_OUTPUT3))
