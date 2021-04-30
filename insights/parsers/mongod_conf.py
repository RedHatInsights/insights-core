"""
MongodbConf - files - Configuration files for MongoDB
=====================================================

This module contains the following files:
    ``/etc/mongod.conf``,
    ``/etc/mongodb.conf`` ,
    ``/etc/opt/rh/rh-mongodb26/mongod.conf``
    ``/etc/opt/rh/rh-mongodb34/mongod.conf``

They are provided by package mongodb-server, rh-mongodb26-mongodb-server or
rh-mongodb34-mongodb-server.
These MongoDB configuration files may use the **YAML** format
or the standard **key-value pair** format.


Sample input(YAML format)::

    systemLog:
      destination: file
      logAppend: true
      path: /var/log/mongodb/mongod.log

    # Where and how to store data.
    storage:
      dbPath: /var/lib/mongo
      journal:
        enabled: true


Sample input(key-value pair format)::

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


Examples:

    >>> mongod_conf1 = shared[MongodConf]
    >>> mongod_conf2 = shared[MongodConf]
    >>> MongodbConf1.is_yaml
    True
    >>> MongodbConf2.is_yaml
    False
    >>> mongod_conf1.fork
    True
    >>> mongod_conf2.fork
    'true'
    >>> mongod_conf1.dbpath
    '/var/lib/mongo'
    >>> mongod_conf2.dbpath
    '/var/lib/mongo'
    >>> mongod_conf1.get("systemlog", {}).get("logAppend")
    True
    >>> MongodbConf2.get("logappend")
    'true'

"""

import yaml
from .. import parser, Parser, LegacyItemAccess, get_active_lines
from ..parsers import ParseException, split_kv_pairs
from ..specs import Specs


@parser(Specs.mongod_conf)
class MongodbConf(Parser, LegacyItemAccess):
    """
    Parse the ``/etc/mongod.conf`` config file in key-value pair or YAML format.
    Make several frequently used config options as properties.

    Raises:
        ParseException: Raised when any problem parsing the file content.

    Attributes:
        is_yaml (boolean): True if this is a yaml format file.
    """
    def parse_content(self, content):
        a_content = get_active_lines(content)
        if not a_content:
            raise ParseException("mongod.conf is empty or all lines are comments")
        self.is_yaml = self._file_type_is_yaml(a_content)
        try:
            if self.is_yaml:
                self.data = yaml.safe_load('\n'.join(content))
            else:
                self.data = split_kv_pairs(content, use_partition=True)
        except Exception as e:
            raise ParseException('mongod conf parse failed: %s', e)

    def _file_type_is_yaml(self, content):
        """
        Return True if the file type is YAML.
        Return False means this file will be handled in key-value pair format.

        Why 0.9?
            The normal key-value pair format file would always has the '='
            in each line. Use 0.9 rather than 1 here, just in case there're
            any unexpected lines with wrong settings.
        """

        cnt = sum([1 for line in content if "=" in line])
        percent = float(cnt) / len(content)
        return True if percent < 0.9 else False

    @property
    def bindip(self):
        """
        Return option value of `net.bindIp` if a yaml conf and `bind_ip` if a
        key-value pair conf.
        """
        if self.is_yaml:
            return self.get('net', {}).get('bindIp')
        else:
            return self.get('bind_ip')

    @property
    def port(self):
        """
        Return option value of `net.port` if a yaml conf and `port` if a
        key-value pair conf.
        """
        if self.is_yaml:
            return self.get('net', {}).get('port')
        else:
            return self.get('port')

    @property
    def dbpath(self):
        """
        Return option value of `storage.dbPath` if a yaml conf and `dbPath`
        if a key-value pair conf.
        """
        if self.is_yaml:
            return self.get('storage', {}).get('dbPath') or self.get('storage.dbPath')
        else:
            return self.get('dbpath')

    @property
    def fork(self):
        """
        Return option value of `processManagement.fork` if a yaml conf and
        `fork` if a key-value pair conf.
        """
        if self.is_yaml:
            return self.get('processManagement', {}).get('fork')
        else:
            return self.get('fork')

    @property
    def pidfilepath(self):
        """
        Return option value of `processManagement.pidFilePath` if a yaml conf
        and `pidFilePath` if a key-value pair conf.
        """
        if self.is_yaml:
            return self.get('processManagement', {}).get('pidFilePath')
        else:
            return self.get('pidfilepath')

    @property
    def syslog(self):
        """
        Return option value of `systemLog.destination` if a yaml conf, this
        can be 'file' or 'syslog'. Return value of `syslog` if a key-value pair
        conf, 'true' means log to syslog.
        Return None means value is not specified in configuration file.
        """
        if self.is_yaml:
            return self.get('systemLog', {}).get('destination')
        else:
            return self.get('syslog')

    @property
    def logpath(self):
        """
        Return option value of `systemLog.path` if a yaml conf and `logpath`
        if a key-value pair conf.
        """
        if self.is_yaml:
            return self.get('systemLog', {}).get('path')
        else:
            return self.get('logpath')
