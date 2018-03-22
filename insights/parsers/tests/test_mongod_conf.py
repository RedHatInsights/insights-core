import pytest

from insights.tests import context_wrap
from insights.parsers import ParseException
from insights.parsers.mongod_conf import MongodbConf


NORMAL_CONF = """
# mongodb.conf - generated from Puppet

#where to log
logpath=/var/log/mongodb/mongodb.log
logappend=true
# Set this option to configure the mongod or mongos process to bind to and
# listen for connections from applications on this address.
# You may concatenate a list of comma separated values to bind mongod to multiple IP addresses.
bind_ip = 127.0.0.1
# fork and run in background
fork=true
dbpath=/var/lib/mongodb
# location of pidfile
pidfilepath=/var/run/mongodb/mongodb.pid
# Enables journaling
journal = true
# Turn on/off security.  Off is currently the default
noauth=true
abc=
""".strip()


NORMAL_CONF_V1 = """
=/var/log/mongodb/mongodb.log
logappend=true # noauth=true
""".strip()


YAML_CONF = """
# mongod.conf

# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# Where and how to store data.
storage:
  dbPath: /var/lib/mongo
  journal:
    enabled: true
#  engine:
#  mmapv1:
#  wiredTiger:

# how the process runs
processManagement:
  fork: true  # fork and run in background
  pidFilePath: /var/run/mongodb/mongod.pid  # location of pidfile

# network interfaces
net:
  port: 27017
  #bindIp: 127.0.0.1  # Listen to local interface only, comment to listen on all interfaces.
  #bindIp: 127.0.0.1  # Listen to local interface only, comment to listen on all interfaces.


#security:

#operationProfiling:

#replication:

#sharding:

## Enterprise-Only Options

#auditLog:

#snmp:
""".strip()

YAML_CONF_UNPARSABLE = """
systemLog:
  destination: file
  logAppend: true
  port=27017

""".strip()


def test_mongodb_conf():

    result = MongodbConf(context_wrap(YAML_CONF))
    assert result.get("security") is None
    assert result.get("processManagement") == {
            'fork': True,
            'pidFilePath': '/var/run/mongodb/mongod.pid'}
    assert result.is_yaml is True
    assert result.port == 27017
    assert result.bindip is None
    assert result.dbpath == '/var/lib/mongo'
    assert result.fork is True
    assert result.pidfilepath == '/var/run/mongodb/mongod.pid'
    assert result.syslog == 'file'
    assert result.logpath == '/var/log/mongodb/mongod.log'

    result = MongodbConf(context_wrap(NORMAL_CONF))
    assert result.is_yaml is False
    assert result.port is None
    assert result.bindip == '127.0.0.1'
    assert result.dbpath == '/var/lib/mongodb'
    assert result.fork == 'true'
    assert result.pidfilepath == '/var/run/mongodb/mongodb.pid'
    assert result.syslog is None
    assert result.logpath == '/var/log/mongodb/mongodb.log'
    assert result.get("abc") == ''
    assert result.get("def") is None

    result = MongodbConf(context_wrap(NORMAL_CONF_V1))
    assert result.is_yaml is False
    assert len(result.data) == 2
    assert result.get("logappend") == 'true'

    with pytest.raises(ParseException) as e:
        MongodbConf(context_wrap(YAML_CONF_UNPARSABLE))
    assert "mongod conf parse failed:" in str(e.value)

    # add test for empty mongod.conf for "ZeroDivisionError: float division by zero"
    with pytest.raises(ParseException) as e:
        MongodbConf(context_wrap("#this is empty"))
    assert "mongod.conf is empty or all lines are comments" in str(e.value)
