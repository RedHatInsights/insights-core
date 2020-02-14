import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import satellite_mongodb_storage_engine


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


def test_doc_examples():
    output = satellite_mongodb_storage_engine.SatelliteMongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT1))
    globs = {
        'satellite_storage_engine': output
    }
    failed, tested = doctest.testmod(satellite_mongodb_storage_engine, globs=globs)
    assert failed == 0


def test_no_storage_engine():
    with pytest.raises(SkipException): 
        satellite_mongodb_storage_engine.SatelliteMongoDBStorageEngine(context_wrap(MONGO_PULP_STORAGE_ENGINE_OUTPUT2))
