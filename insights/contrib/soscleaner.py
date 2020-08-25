# Copyright (C) 2013  Jamie Duncan (jduncan@redhat.com)

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# File Name : soscleaner.py
# Creation Date : 10-01-2013
# Created By : Jamie Duncan
# Purpose : an sosreport and data set obfuscation tool

import os
import hashlib
import re
import errno
import stat
import sys
import uuid
import shutil
import tempfile
import logging
import tarfile
from insights.contrib.ipaddress import IPv4Network, IPv4Address, IPv6Network, IPv6Address

from random import randint
from six.moves import configparser
import subprocess

import six
if six.PY3:
    from builtins import str
    from builtins import range
    from builtins import object
else:
    from __builtin__ import str
    from __builtin__ import range
    from __builtin__ import object


class SOSCleaner(object):
    """
    A class to parse through an sosreport or generic dataset to begin the
    cleaning and obfuscation process required in many industries.
    """

    def __init__(self, quiet=False):

        self.name = 'soscleaner'
        self.quiet = quiet
        self.domain_count = 0
        self.domains = ['redhat.com', 'localhost.localdomain']
        self.short_domains = ['localdomain', 'localhost']
        self.domainname = None
        self.report_dir = '/tmp'
        self.version = '0.4.4'
        self.false_positives = [
            'installed-debs',
            'installed_rpms',
            'sos_commands/dpkg',
            'sos_commands/rpm',
            'sos_commands/snappy/snap_list_--all',
            'sos_commands/snappy/snap_--version'
        ]
        self.loglevel = 'INFO'
        self.net_db = list()  # Network Information database
        self.ip_db = list()
        if six.PY3:
            self.default_net = IPv4Network('128.0.0.0/8')
        else:
            self.default_net = IPv4Network(unicode('128.0.0.0/8'))
        self.default_netmask = self.default_net.prefixlen
        # we'll have to keep track of how many networks we have so we don't have to count them each time we need to create a new one.
        self.net_count = 0
        self.net_metadata = dict()

        self.net_metadata[self.default_net.network_address.compressed] = dict()
        self.net_metadata[self.default_net.network_address.compressed]['host_count'] = 0

        # Hostname obfuscation information
        self.hn_db = dict()  # hostname database
        self.hostname_count = 0
        self.hostname = None

        self.mac_db = dict()  # mac address database
        self.mac_count = 0

        # Domainname obfuscation information
        self.dn_db = dict()  # domainname database
        # right now this needs to be a 2nd level domain
        # examples: foo.com, example.com, domain.org
        self.root_domain = 'obfuscateddomain.com'

        # Keyword obfuscation information
        self.keywords_file = list()
        self.keywords = list()
        self.kw_db = dict()  # keyword database
        self.kw_count = 0

        # obfuscating users from the last command, per rfe #79
        self.users_file = 'sos_commands/last/lastlog_-u_1000-60000'
        self.user_db = dict()
        self.user_count = 0
        self.config_file = '/etc/soscleaner.conf'
        self._read_early_config_options()
        self.obfuscate_macs = True  # issue #98

    def _check_uid(self):
        """Ensures soscleaner is running as root. This isn't required for soscleaner,
        but sosreports are run as root and root tends to own the files inside the
        sosreport tarball
        """

        try:  # pragma: no cover
            if os.getuid() != 0:
                self.logger.warning(
                    "soscleaner must be executed by the root user in the same manner as sosreport")
                self.logger.warning("soscleaner cannot continue. Exiting...")

                sys.exit(8)

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "UID_ERROR - unable to run SOSCleaner - you do not appear to be the root user")

    def _read_early_config_options(self):
        """Reads an optional configuration file to load often-used defaults for
        domains, networks, keywords, etc. If a config file is present and command-line
        parameters are passed in, they will be additive, with the config file being
        read in first.
        """

        try:
            config = configparser.ConfigParser()
            if os.path.exists(self.config_file):
                config.read(self.config_file)

                # load in default config values
                if config.has_option('Default', 'loglevel'):
                    self.loglevel = config.get('Default', 'loglevel').upper()
                if config.has_option('Default', 'root_domain'):
                    self.root_domain = config.get('Default', 'root_domain')
                if config.has_option('Default', 'quiet'):
                    self.quiet = config.get('Default', 'quiet')
                return True

            else:
                return True

        except OSError as e:  # pragma: no cover
            pass

    def _read_later_config_options(self):
        """Reads an optional configuration file to load often-used defaults for
        domains, networks, keywords, etc. If a config file is present and command-line
        parameters are passed in, they will be addadtive, with the config file being
        read in first.
        """

        try:
            config = configparser.ConfigParser()
            if os.path.exists(self.config_file):
                config.read(self.config_file)
                self.logger.con_out(
                    "Loading config file for default values - %s", self.config_file)
                if config.has_section('DomainConfig'):
                    domains = config.get('DomainConfig', 'domains').split(',')
                    for d in domains:
                        self.domains.append(d)
                        self.logger.con_out(
                            "Loading domains from config file - %s", d)
                    else:
                        self.logger.con_out(
                            "No config found - DomainConfig.domains")
                else:
                    self.logger.con_out(
                        "No config file section found - DomainConfig")

                if config.has_section('KeywordConfig'):
                    if config.has_option('KeywordConfig', 'keywords'):
                        keywords = config.get('KeywordConfig', 'keywords')
                        kw = keywords.split(',')
                        for k in kw:
                            self.keywords.append(k.strip())
                    else:
                        self.logger.con_out(
                            "No config found - KeywordConfig.keywords")
                    if config.has_option('KeywordConfig', 'keyword_files'):
                        keyword_files = config.get(
                            'KeywordConfig', 'keyword_files').split(',')
                        for f in keyword_files:
                            self.keywords_file.append(f)
                            self.logger.con_out(
                                "Adding keyword file from config file - %s", f)
                    else:
                        self.logger.con_out(
                            "No config found - KeywordConfig.keyword_files")

                # load in networks
                # we need them to be in a list so we can process
                # them individually
                # each network should be a CIDR notation
                # string, eg 192.168.1.0/24
                if config.has_section('NetworkConfig'):
                    if config.has_option('NetworkConfig', 'networks'):
                        networks = config.get('NetworkConfig', 'networks')
                        networks = networks.split(',')
                        for network in networks:
                            self._ip4_add_network(network)
                            self.logger.con_out(
                                "Adding network from config file - %s", network)
                    else:
                        self.logger.con_out(
                            "No config found - NetworkConfig.networks")

                if config.has_section('MacConfig'):
                    if config.has_option('MacConfig', 'obfuscate_macs'):
                        self.obfuscate_macs = bool(
                            config.get('MacConfig', 'obfuscate_macs'))

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            self.logger.con_out(
                "READ_CONFIG_OPTIONS_ERROR - Unable to load configs from file %s - Continuing without those values", self.config_file)

    def _extract_file_data(self, filename):
        """Extracts data from a file and return the data"""
        try:
            fh = open(filename, 'r')
            data = fh.readlines()
            fh.close()

            return data

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception("FILE_OPEN_ERROR - unable to open %s", filename)

    def _skip_file(self, d, files):
        """The function passed into shutil.copytree to ignore certain
        patterns and filetypes
        Currently Skipped:
        1) Directories - handled by copytree
        2) Symlinks - handled by copytree
        3) Write-only files (stuff in /proc)
        Binaries (can't scan them)
        Sockets and FIFO files. Scanning them locks up the copying.
        """
        def confirm_text_file(filename):
            """I know this is an epic hack, but I've seen a _ton_
            of inconsistency around different distribution's builds
            of python-magic. Until it stabilizes, I'm just going to
            hack around it.
            """
            try:
                command = "file %s" % filename
                filetype = os.popen(command).read().strip(
                    '\n').split(':')[1].strip().lower()
                if 'text' in filetype or 'json' in filetype:
                    return True
                else:
                    return False
            except Exception as e:  # pragma: no cover
                self.logger.exception(e)
                raise Exception(
                    "CONFIRM_TEXT_FILE_ERROR - Cannot confirm file type - %s", filename)

        skip_list = []
        for f in files:
            f_full = os.path.join(d, f)
            if not os.path.isdir(f_full):
                if not os.path.islink(f_full):
                    mode = os.stat(f_full).st_mode
                    if stat.S_ISSOCK(mode) or stat.S_ISFIFO(mode):
                        skip_list.append(f)
                    if not confirm_text_file(f_full):  # if it's not a text file
                        skip_list.append(f)

        return skip_list

    def _start_logging(self, filename):
        """Creates the logging objects and starts a logging instance."""
        # will get the logging instance going
        loglevel_config = '%s' % self.loglevel

        # i'd like the stdout to be under another logging name than 'con_out'
        console_log_level = 25  # between INFO and WARNING
        quiet = self.quiet
        logging.addLevelName(console_log_level, "CONSOLE")

        def con_out(self, message, *args, **kws):   # pragma: no cover
            if not quiet:
                self._log(console_log_level, message, args, **kws)

        logging.Logger.con_out = con_out

        logging.basicConfig(filename=filename,
                            level=logging.getLevelName(loglevel_config),
                            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                            datefmt='%m-%d %H:%M:%S'
                            )
        if not self.quiet:  # pragma: no cover
            console = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s %(name)s %(levelname)s: %(message)s', '%m-%d %H:%M:%S')
            console.setFormatter(formatter)
            console.setLevel(console_log_level)
        self.logger = logging.getLogger(__name__)
        if not self.quiet:
            self.logger.addHandler(console)  # pragma: no cover

        self.logger.con_out("Log File Created at %s" % filename)

    def _prep_environment(self):
        """Creates the needed definitions to identify the unique
        soscleaner runs
        It creates a 16 character UUID, then uses that to
        create an origin_path to define where the temporary working
        files are stored, a dir_path that is where the
        obfuscated files are located, and a session value,
        which is used in multiple locations to identify objects
        for a given soscleaner run
        """

        # we set up our various needed directory structures, etc.
        # 16 digit random string
        ran_uuid = str(uuid.uuid4().int)[:16]
        # Gather data into its own soscleaner session directory
        self.report_dir += '/' + 'soscleaner-' + ran_uuid
        os.makedirs( self.report_dir, 0o700 )
        # the origin dir we'll copy the files from
        origin_path = os.path.join(
            self.report_dir, "soscleaner-origin-%s" % ran_uuid)
        # the dir we will put our cleaned files into
        dir_path = os.path.join(self.report_dir, "soscleaner-%s" % ran_uuid)
        # short-hand for the soscleaner session to create reports, etc.
        session = os.path.join(self.report_dir, "soscleaner-%s" % ran_uuid)
        # the primary logfile
        logfile = os.path.join(self.report_dir, "%s.log" % session)

        return origin_path, dir_path, session, logfile, ran_uuid

    def _extract_sosreport(self, path):
        """Extracts an sosreport, accounting for all common compression algorithms
        as well as working with uncompressed directories and single files.
        """
        def get_compression_sig(filename):
            try:
                """I know this is an epic hack, but I've seen a _ton_ of inconsistency around different
                distribution's builds of python-magic. Until it stabilizes, I'm just going to hack around it.
                """
                 
                command = "file %s" % filename
                compression_type = os.popen(command).read().strip(
                    '\n').split(':')[1].strip().lower()
                return compression_type

            except Exception as e:  # pragma: no cover
                self.logger.exception(e)
                raise Exception(
                    "GET_COMPRESSION_SIG_ERROR: Unable to verify compression sig - %s", filename)

        try:
            self.logger.con_out("Beginning SOSReport Extraction")
            if os.path.isdir(path):
                self.logger.info(
                    '%s appears to be a directory, no extraction required - continuing', path)
                # Clear out origin_path as we don't have one
                self.origin_path = None
                return path
            else:
                try:
                    compression_sig = get_compression_sig(path)
                    if compression_sig == 'xz compressed data':
                        try:
                            self.logger.info(
                                'Data Source Appears To Be LZMA Encrypted Data - decompressing into %s', self.origin_path)
                            self.logger.info(
                                'LZMA Hack - Creating %s', self.origin_path)
                            os.makedirs( self.origin_path, 0o755 )
                            subprocess.Popen(
                                ["tar", "-xJf", path, "-C", self.origin_path]).wait()

                            return_path = os.path.join(
                                self.origin_path, os.listdir(self.origin_path)[0])

                            return return_path

                        except Exception as e:  # pragma: no cover
                            self.logger.exception(e)
                            raise Exception(
                                'DecompressionError, Unable to decrypt LZMA compressed file %s', path)

                    # the tarfile module handles other compression types.
                    # so we can just use that
                    else:
                        p = tarfile.open(path, 'r')
                        self.logger.info(
                            'Data Source Appears To Be %s - decompressing into %s', compression_sig, self.origin_path)

                        p.extractall(self.origin_path)
                        return_path = os.path.join(
                            self.origin_path, os.path.commonprefix(p.getnames()))

                        return return_path

                except Exception as e:    # pragma: no cover
                    self.logger.exception(e)
                    raise Exception(
                        "DeCompressionError: Unable to De-Compress %s into %s", path, self.origin_path)

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CompressionError: Unable To Determine Compression Type')

    ################################
    #  User Functions  #
    ################################

    def _process_user_option(self, users):
        """Adds users specified from the command line to the user_db object"""

        try:
            for username in users:
                new_user = self._user2db(username)
                self.logger.con_out(
                    "Adding user from the command line - %s > %s", username, new_user)

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "PROCESS_USER_OPTION_ERROR: unable to add user to user database")

    def _sub_username(self, line):
        """Accepts a line from a file as input and replaces all occurrences of the users in the
        user_db with the obfuscated values.
        Returns the obfuscated line.
        """

        try:
            if self.user_count > 0:    # we have obfuscated keywords to work with
                for user, o_user in list(self.user_db.items()):
                    line = re.sub(r'\b%s\b(?i)' % user, o_user, line)
                    self.logger.debug(
                            "Obfuscating User - %s > %s", user, o_user)

            return line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'SUB_USERNAME_ERROR: Unable to obfuscate usernames on line - %s', line)

    def _create_random_username(self):
        """Generates a random, unique obfuscated user ID and returns it"""

        def _randomizer():
            return "obfuscateduser%s" % randint(1,1000000)

        test_user = _randomizer()
        if test_user in list(self.user_db.values()):
            while test_user in list(self.user_db.values()):
                self.logger.debug("Duplicate Obfuscated Hostname. Retrying - %s", test_user)
                test_user = _randomizer()
                if test_user not in list(self.user_db.values()):
                    return test_user
        else:
            return test_user

    def _user2db(self, username):
        """Takes a username and adds it to the user_db with an obfuscated partner.
        If the user hasn't been encountered before, it will add it to the database
        and return the obfuscated partner entry.
        If the user is already in the database it will return the obfuscated username
        """
        try:
            o_user = self.user_db.get(username)
            if o_user is None:  # no match, so we need to add to the database
                # new username, so we increment the counter to get the user's obfuscated name
                self.user_count += 1
                o_user = self._create_random_username()
                self.logger.info(
                    "Adding new obfuscated user: %s > %s", username, o_user)
                self.user_db[username] = o_user

            return o_user

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "USER_TO_DB_ERROR: unable to add user %s to database", username)

    def _process_users_file(self):
        """Uses the 'last' output from an sosreport and generate a list of usernames to obfuscate in log files, etc.
        By default it looks for the last file from an sosreport. But it can process any line-delimited list of users
        From RFE #79
        """

        # Users and entries that we don't want to obfuscate that could show up in lastlog
        ignored_users = ('Username',
                         'ubuntu'
                         )

        # we're not calling this function from an option on the cli, we're just running it as part of __init__

        try:
            users_file = os.path.join(self.dir_path, self.users_file)
            # check to make sure users_file is there and we can access it
            if os.path.exists(users_file):
                self.logger.con_out(
                    "Processing output from user file - %s", users_file)
                data = self._extract_file_data(users_file)
                sorted_users = list()

                # first, we get out the unique user entries
                for line in data:
                    if len(line) > 1:  # there are some blank lines at the end of the last output
                        sorted_users.append(line.split()[0])

                # then we add them to the obfuscation database
                for user in sorted_users:
                    if user not in ignored_users:
                        self.logger.con_out("Obfuscating user %s", user)
                        self._user2db(user)

                return True

            else:
                self.logger.con_out(
                    "Unable to locate user file - %s", users_file)
                self.logger.con_out("Continuing without processing users file")

                return False

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "PROCESS_USERS_FILE_ERROR: unable to add file - %s", self.users_file)

    ################################
    #   IP Obfuscation Functions   #
    ################################

    def _sub_ip(self, line):
        """Substitutes a found IP with its corresponding obfuscated partner.
        This is called in the self._clean_line function, along with user _sub_*
        functions to scrub a given line in a file. It scans a given line and if
        an IP exists, it obfuscates the IP using _ip4_2_db and returns the altered
        line
        """
        try:
            pattern = r"(((\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[1-9]))(\.(\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[0-9])){3})"
            ips = [each[0] for each in re.findall(pattern, line)]
            if len(ips) > 0:
                for ip in ips:
                    new_ip = self._ip4_2_db(ip)
                    self.logger.debug("Obfuscating IP - %s > %s", ip, new_ip)
                    line = line.replace(ip, new_ip)
            return line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception("SUB_IP_ERROR: Unable to obfuscate IP address")

    #############################
    #   Formatting Functions    #
    #############################

    def _get_version(self):
        """Prints out soscleaner version"""

        self.logger.con_out(
            "SOSCleaner version: %s" % self.version)

    def _get_disclaimer(self):
        """Prints out a disclaimer at the beginning of each soscleaner run"""

        self.logger.con_out(
            "%s is a tool to help obfuscate sensitive information from an existing sosreport." % self.name)  # pragma: no cover
        self.logger.con_out(
            "Please review the content before passing it along to any third party.")  # pragma: no cover

    ###########################
    #   Reporting Functions   #
    ###########################
    def _create_mac_report(self):
        """Creates a report of MAC addresses and their obfuscated counterparts"""
        try:
            mac_report_name = os.path.join(
                self.report_dir, "%s-mac.csv" % self.session)
            self.logger.con_out(
                'Creating MAC address Report - %s', mac_report_name)
            mac_report = open(mac_report_name, 'w')
            mac_report.write('Original MAC Address,Obfuscated MAC Address\n')
            if len(self.mac_db) > 0:
                for k, v in list(self.mac_db.items()):
                    mac_report.write('%s,%s\n' % (k, v))
            else:
                mac_report.write('None,None\n')
            mac_report.close()
            os.chmod(mac_report_name, 0o600)
            self.logger.info('Completed MAC Address Report')

            self.mac_report = mac_report_name

        except Exception as e:  # pragma no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_MAC_REPORT_ERROR: Unable to create report - %s', mac_report_name)

    def _create_kw_report(self):
        """Creates a report of keywords and their obfuscated counterparts"""
        try:
            kw_report_name = os.path.join(
                self.report_dir, "%s-keyword.csv" % self.session)
            self.logger.con_out(
                'Creating keyword address Report - %s', kw_report_name)
            kw_report = open(kw_report_name, 'w')
            kw_report.write('Original Keyword,Obfuscated Keyword\n')
            if self.kw_count > 0:
                for keyword, o_keyword in list(self.kw_db.items()):
                    kw_report.write('%s,%s\n' % (keyword, o_keyword))
            else:
                kw_report.write('None,None\n')
            kw_report.close()
            os.chmod(kw_report_name, 0o600)
            self.logger.info('Completed Keyword Report')

            self.kw_report = kw_report_name

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_KW_REPORT_ERROR: unable to create report - $%s', kw_report_name)

    def _create_un_report(self):
        """Creates a report of usernames and their obfuscated counterparts. 
        """
        try:
            un_report_name = os.path.join(
                self.report_dir, "%s-username.csv" % self.session)
            self.logger.con_out(
                'Creating Username Report - %s', un_report_name)
            un_report = open(un_report_name, 'w')
            un_report.write('Original Username,Obfuscated Username\n')
            for k, v in list(self.user_db.items()):
                un_report.write('%s,%s\n' % (k, v))
            un_report.close()
            os.chmod(un_report_name, 0o600)

            self.un_report = un_report_name
        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_USERNAME_REPORT_ERROR: Unable to create report - %s', un_report_name)

    def _create_hn_report(self):
        """Creates a report of hostnames and their obfuscated counterparts"""
        try:
            hn_report_name = os.path.join(
                self.report_dir, "%s-hostname.csv" % self.session)
            self.logger.con_out(
                'Creating Hostname Report - %s', hn_report_name)
            hn_report = open(hn_report_name, 'w')
            hn_report.write('Original Hostname,Obfuscated Hostname\n')
            if self.hostname_count > 0:
                for k, v in list(self.hn_db.items()):
                    hn_report.write('%s,%s\n' % (k, v))
            else:
                hn_report.write('None,None\n')
            os.chmod(hn_report_name, 0o600)
            hn_report.close()
            self.logger.info('Completed Hostname Report')

            self.hn_report = hn_report_name
        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_HN_REPORT_ERROR: Unable to create report - %s', hn_report_name)

    def _create_dn_report(self):
        """Creates a report of domain names and their obfuscated conterparts"""
        try:
            dn_report_name = os.path.join(
                self.report_dir, "%s-dn.csv" % self.session)
            self.logger.con_out(
                'Creating Domainname Report - %s', dn_report_name)
            dn_report = open(dn_report_name, 'w')
            dn_report.write('Original Domain,Obfuscated Domain\n')
            if self.domain_count > 0:
                for domain, o_domain in list(self.dn_db.items()):
                    dn_report.write('%s,%s\n' % (domain, o_domain))
            else:
                dn_report.write('None,None\n')
            dn_report.close()
            os.chmod(dn_report_name, 0o600)
            self.logger.info('Completed Domainname Report')

            self.dn_report = dn_report_name

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_DN_REPORT_ERROR: Unable to create report - %s', dn_report_name)

    def _create_ip_report(self):
        """Creates a report of IP addresses and their obfuscated counterparts"""
        try:
            ip_report_name = os.path.join(
                self.report_dir, "%s-ip.csv" % self.session)
            self.logger.con_out('Creating IP Report - %s', ip_report_name)
            ip_report = open(ip_report_name, 'w')
            ip_report.write('Original IP,Obfuscated IP\n')
            for i in self.ip_db:
                ip_report.write('%s,%s\n' % (i[0], i[1]))
            ip_report.close()
            os.chmod(ip_report_name, 0o600)
            self.logger.info('Completed IP Report')

            self.ip_report = ip_report_name

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_IP_REPORT_ERROR: Unable to create report - %s', ip_report_name)

    def _create_sos_report(self):
        """Creates a report of original sosreport tarball and its obfuscated counterpart"""
        try:
            sos_report_name = os.path.join(
                self.report_dir, "%s-sosreport.csv" % self.session)
            self.logger.con_out('Creating sosreport Report - %s', sos_report_name)
            sos_report = open(sos_report_name, 'w')
            sos_report.write('Original Sosreport,Obfuscated Sosreport\n')
            sos_report.write('%s,%s.tar.gz\n' % (self.sosreport_filename, self.session))
            sos_report.close()
            os.chmod(sos_report_name, 0o600)
            self.logger.info('Completed Sosreport Report')

            self.sos_report = sos_report_name

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_SOS_REPORT_ERROR: Unable to create report - %s', sos_report_name)

    def _create_reports(self):
        """Creates the reports at the end of an soscleaner run"""

        self._create_ip_report()  # pragma: no cover
        self._create_hn_report()  # pragma: no cover
        self._create_dn_report()  # pragma: no cover
        # self._create_un_report()  # pragma: no cover
        # self._create_mac_report()  # pragma: no cover
        # self._create_kw_report()  # pragma: no cover
        # self._create_sos_report()  # pragma: no cover
        # os.chmod(self.logfile, 0o600)

    #############################
    #   MAC Address functions   #
    #############################

    def _sub_mac(self, line):
        """Finds potential MAC addresses and obfuscates them in a single line."""
        try:
            pattern = re.compile(r'(?:[0-9a-fA-F]:?){12}')
            macs = re.findall(pattern, line)
            if len(macs) > 0:
                for mac in macs:
                    new_mac = self._mac2db(mac)
                    self.logger.debug(
                        "Obfuscating MAC address - %s > %s", mac, new_mac)
                    line = line.replace(mac, new_mac)
            return line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception("SUB_MAC_ERROR: Unable to obfuscate MAC address")

    def _mac2db(self, mac):
        """Adds an MAC address to the MAC database and returns the obfuscated
        entry, or returns the existing obfuscated MAC entry.
        """
        try:
            o_mac = self.mac_db.get(mac)
            if o_mac is None:  # no match: we have to add it to the db
                # using this lambda to create a valid randomized mac address is
                # documented at https://www.commandlinefu.com/commands/view/7245/generate-random-valid-mac-addresses
                # many thanks for putting that little thought together
                o_mac = ':'.join(['%02x' % x for x in [randint(0, 255) for x in list(range(6))]])
                self.logger.debug(
                    "Creating new obfuscated MAC address: %s > %s", mac, o_mac)
                self.mac_db[mac] = o_mac

            return o_mac

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "MAC2DB_ERROR: unable to add MAC to database - %s", mac)

    ###########################
    #   Hostname functions    #
    ###########################

    def _hn2db(self, host):
        """Adds a hostname for a hostname for an included domain or return an existing entry.
        It is called by _add_hostnames to verify if the domain is in an included
        domain for obfuscation, and the entry to hn_db, and return the obfuscated value
        """
        try:
            o_host = self.hn_db.get(host)
            if o_host is None:  # no database match
                split_host = host.split('.')
                self.hostname_count += 1  # increment the counter to get the host ID number
                if len(split_host) == 1:  # we have a non-fqdn - typically the host short name
                    o_host = "obfuscatedhost%s" % self.hostname_count
                    self.hn_db[host] = o_host
                elif len(split_host) == 2:  # we have a root domain, a la example.com
                    o_host = self._dn2db(host)
                else:  # a 3rd level domain or higher
                    domain = '.'.join(split_host[1:])
                    o_domain = self._dn2db(domain)
                    o_host = "host%s.%s" % (self.hostname_count, o_domain)
                    self.hn_db[host] = o_host

            if o_host is not None:
                return o_host

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "HN2DB_ERROR: Unable to add hostname to database - %s", host)

    def _get_hostname(self, hostname='hostname'):
        """Gets the hostname from an sosreport. Used at the beginning of an
        SOSCleaner run to set self.hostname and self.domainname
        """

        try:
            hostfile = os.path.join(self.dir_path, hostname)
            fh = open(hostfile, 'r')
            name_list = fh.readline().rstrip().split('.')
            hostname = name_list[0]
            if len(name_list) > 1:
                domainname = '.'.join(name_list[1:len(name_list)])
            else:
                domainname = None

            return hostname, domainname

        except IOError as e:  # the 'hostname' file doesn't exist or isn't readable for some reason
            if not self.quiet:  # pragma: no cover
                self.logger.exception(e)

            hostname = None
            domainname = None

            return hostname, domainname

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'GET_HOSTNAME_ERROR: Cannot resolve hostname from %s') % hostfile

    def _validate_domainname(self, hostname):
        """Takes a potential domain name and validates it against the domain database
        (self.dn_db). It takes care to look for higher-level subdomains for the
        domains entered at the beginning of the sosreport run. Logic behind this definition of a valid domain:
        A domain can be a total of 253 characters, per RFC 1035, RFC 1123 and RFC 2181
        Each label can be a maximum of 63 characters
        With 4th, 5th, 6th level domains being more the norm today, I wanted to take as
        broad an interpretation of a domain as I could. SO:
        separated by a word boundary
        the lower domains can be a max of 190 characters, not including dots
        any valid domain character is allowed (alpha, digit, dash)
        the top level domain can be up to 63 characters, and not contain numbers
        With a 200 character limit to the lower domains, technically an 11th level domain
        would not be obfuscated. As for right now, I'm OK with that. Please file an issue
        in Github if you are not.
        Summary:
        Valid domain is defined as
        <word><Up to 200 chars of alpha, digit, dash, and dot>.<Up to 63 chars of alpha></word>
        """
        def _eval_domains(root_domain):
            """Looks for matches of higher-level domains against the existing
            domains in self.dn_db. Returns True if it's a match, and false if
            no match is found. This is used to determine if we should add a new
            subdomain to self.dn_db.
            """
            for known_domain in list(self.dn_db.keys()):
                if known_domain in root_domain:
                    self.logger.debug(
                        "evaluated domain found in database %s > %s", root_domain, known_domain)
                    return True
            return False

        domainname = hostname.split('.')
        domain_depth = len(domainname)
        self.logger.debug("validating domain %s - depth: %s",
                          hostname, domain_depth)
        # The first clause checks for potential domains that are 3rd level
        # domains or higher. If the base domain (everything except the
        # first octet) is already in the database, it adds the host. If
        # the root domain is in the database, but this is a new higher-
        # level domain, it adds the higher-level domain to the database
        # before moving forward with obfuscating the full hostname.
        found_domain = False
        if domain_depth > 2:
            # everything after the hostname is the domain we need to check
            root_domain = '.'.join(domainname[1:domain_depth])
            self.logger.debug("validating domain - %s", root_domain)
            # We try a straigh match first
            o_domain = self._dn2db(root_domain)
            if o_domain is not None:  # we got a straight match
                found_domain = True
            # If we don't get a straight match, then we look to see if
            # it is a subdomain of an already obfuscated domain.
            else:
                add_domain = _eval_domains(root_domain)
                if add_domain:
                    self.logger.debug(
                        "Found new subdomain of %s - %s", root_domain, domainname)
                    found_domain = True
                    o_domain = self._dn2db(root_domain, add_domain=True)

        elif domain_depth == 2:
            o_domain = self.dn_db.get(hostname)
            if o_domain:
                self.logger.debug(
                    "Domain found in domain database - %s", domainname)
                found_domain = True

        return found_domain

    def _sub_hostname(self, line):
        """Replaces the exact hostname and all instances of the domain name with
        their obfuscated alternatives. Also handles auto-creation of subdomains
        for known domains. Example: if redhat.com is in the domain database,
        access.redhat.com and registry.redhat.com will both be obfuscated as
        unique domain entries.
        """
        # self.logger.debug("Processing Line - %s", line)
        potential_hostnames = re.findall(
            r'\b[a-zA-Z0-9-\.]{1,200}\.[a-zA-Z]{1,63}\b', line)
        try:
            for hostname in potential_hostnames:
                hostname = hostname.lower()
                self.logger.debug(
                    "Verifying potential hostname - %s", hostname)
                domain_found = self._validate_domainname(hostname)

                # If we have a potential match that is a host on a domain that
                # we care about, we regex it out of the line.
                if domain_found:
                    o_hostname = self._hn2db(hostname)
                    line = re.sub(r'\b%s\b(?i)' % hostname, o_hostname, line)

            # Now that the hard work is done, we account for the handful of
            # single-word "short domains" that we care about. We start with
            # the hostname.
            if self.hostname is not None:
                o_host = self._hn2db(self.hostname)
                line = re.sub(r'\b%s\b(?i)' % self.hostname, o_host, line)

            # There are a handful of short domains that we want to obfuscate
            # Things like 'localhost' and 'localdomain'
            # They are kept in self.short_domains and added to the domain
            # database. They won't match the potential_hostnames regex because
            # they're only 1 word, so we handle them here.
            for domain in self.short_domains:
                o_host = self._hn2db(domain)
                line = re.sub(r'\b%s\b(?i)' % domain, o_host, line)

            return line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "SUB_HOSTNAME_ERROR: Unable to obfuscate hostnames on line - %s", line)

    ############################
    #   Filesystem functions   #
    ############################

    def _clean_line(self, line, filename):
        """Returns a line with obfuscations for all covered data types:
        hostname, ip, user, keyword, and MAC address. The filename is passed in
        so we can know whether or not to obfuscate IP addresses. IP obfuscation
        is excluding in a few files where RPM version numbers cause false
        positives and are known to not contain IP address information.
        """

        try:
            process_obfuscation = True
            # We want to skip the files in self.false_positives for all
            # obfuscation but keywords because they don't have any sensible
            # info in them and they generate a lot of false positives that
            # much up the obfuscation and confuse people when they're working
            # with the files
            # Issues #60 & #101
            for false_positive in self.false_positives:
                if false_positive in filename:
                    process_obfuscation = False
            new_line = self._sub_keywords(line)  # Keyword Substitution
            if self.obfuscate_macs is True:
                new_line = self._sub_mac(new_line)  # MAC address obfuscation
            if process_obfuscation:
                new_line = self._sub_hostname(
                    new_line)  # Hostname substitution
                new_line = self._sub_ip(new_line)  # IP substitution
                new_line = self._sub_username(
                    new_line)  # Username substitution

            return new_line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception("CLEAN_LINE_ERROR: Cannot Clean Line - %s" % line)

    def _clean_file(self, f):
        """Takes a given file path, scrubs it, and saves a new copy of
         the obfuscated file in the same location
         """
        if os.path.exists(f) and not os.path.islink(f):
            tmp_file = tempfile.TemporaryFile()
            try:
                data = self._extract_file_data(f)
                if len(data) > 0:  # if the file isn't empty:
                    for l in data:
                        # self.logger.debug("Obfuscating Line - %s", l)
                        new_l = self._clean_line(l, f)
                        if six.PY3:
                            tmp_file.write(new_l.encode('utf-8'))
                        else:
                            tmp_file.write(new_l)

                    tmp_file.seek(0)

            except Exception as e:  # pragma: no cover
                self.logger.exception(e)
                raise Exception(
                    "CLEAN_FILE_ERROR: Unable to obfuscate file - %s" % f)

            try:
                if len(data) > 0:
                    new_fh = open(f, 'wb')
                    for line in tmp_file:
                        new_fh.write(line)
                    new_fh.close()
            except OSError as e:
                # If there's an IO error (disk is full)
                if e.errno == errno.EIO:  # pragma: no cover
                    self.logger.exception(e)
                    self.logger.con_out(
                        "CLEAN_FILE_ERROR: Not enough disk space to complete report obfusation")
                    self.logger.con_out(
                        "CLEAN_FILE_ERROR: Removing partially obfuscated report and other artifacts")
                    self.logger.con_out(
                        "CLEAN_FILE_ERROR: Please remedy the disk pressure and re-run soscleaner")
                    self._clean_up()
            except Exception as e:  # pragma: no cover
                self.logger.exception(e)
                raise Exception(
                    "CLEAN_FILE_ERROR: Unable to write obfuscated file - %s" % f)

            finally:
                tmp_file.close()

    def _add_extra_files(self, files):
        """Incorporates extra files are to be analyzed with an sosreport by
        adding them to the origin path to be analyzed
        """

        try:
            for f in files:
                self.logger.con_out(
                    "adding additional file for analysis: %s" % f)
                fname = os.path.basename(f)
                f_new = os.path.join(self.dir_path, fname)
                shutil.copyfile(f, f_new)
        except IOError as e:
            self.logger.con_out(
                "ExtraFileError: %s is not readable or does not exist. Skipping File" % f)
            self.logger.exception(e)
            pass
        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "ADD_EXTRA_FILES_ERROR: Unable to process extra file - %s" % f)

    def _walk_report(self, folder):
        """Returns a dictonary of dictionaries in the format {directory_name:[file1,file2,filex]}"""

        dir_list = {}
        try:
            for dirName, subdirList, fileList in os.walk(folder):
                x = []
                for fname in fileList:
                    x.append(fname)
                dir_list[dirName] = x

            return dir_list
        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "WALK_REPORT_ERROR: Unable to create file list in folder - %s", folder)

    def _file_list(self, folder):
        """returns a list of file names in an sosreport directory"""
        try:
            rtn = []
            walk = self._walk_report(folder)
            for key, val in list(walk.items()):
                for v in val:
                    x = os.path.join(key, v)
                    rtn.append(x)

            # a count of the files we'll have in the final cleaned sosreport
            self.file_count = len(rtn)
            return rtn

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "FILE_LIST_ERROR: Unable to create file list from directory - %s", folder)

    def _make_dest_env(self):
        """Creates the folder in self.report_dir (defaults to /tmp) to store
        sanitized files and populates it using shutil. These are the files that
        will be scrubbed.
        """
        try:
            shutil.copytree(self.report, self.dir_path,
                            symlinks=True, ignore=self._skip_file)

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "MAKE_DESTINATION_ENV_ERROR: Cannot Create Destination Environment")

    def _create_archive(self):
        """Creates a tar.gz compressed archive of the scrubbed directory"""
        try:
            self.archive_path = os.path.join(
                self.report_dir, "%s.tar.gz" % self.session)
            self.logger.con_out(
                'Creating SOSCleaner Archive - %s', self.archive_path)
            t = tarfile.open(self.archive_path, 'w:gz')
            for dirpath, dirnames, filenames in os.walk(self.dir_path):
                for f in filenames:
                    f_full = os.path.join(dirpath, f)
                    f_archive = f_full.replace(self.report_dir, '')
                    self.logger.debug('adding %s to %s archive',
                                      f_archive, self.archive_path)
                    t.add(f_full, arcname=f_archive)
            os.chmod(self.archive_path, 0o600)  # per #90
        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'CREATE_ARCHIVE_ERROR: Unable to create archive - %s', self.archive_path)

        self._clean_up()
        self.logger.info('Archiving Complete')
        if not self.quiet:  # pragma: no cover
            t.add(self.logfile, arcname=self.logfile.replace(self.report_dir, ''))
        t.close()

    def soscleaner_checksum(self):
        """check MD5 against soscleaner tarball"""
        soscleaner_archive = self.session + ".tar.gz"
        checksum = hashlib.md5(open(soscleaner_archive, 'rb').read()).hexdigest()

        soscleaner_archive_hash = soscleaner_archive + ".md5"
        fp = open(soscleaner_archive_hash, "w")
        fp.write(checksum + "\n")
        self.logger.con_out('md5 checksum is: %s' % checksum)
        fp.close()

    def finalmsg(self):
        """Final message at the end of the soscleaner run"""
        self.logger.con_out('SOSCleaner Complete')

    def _clean_up(self):
        """Cleans up origin directories and other soscleaner processing artifacts"""
        self.logger.info('Beginning Clean Up Process')
        try:
            if self.origin_path:
                self.logger.info(
                    'Removing Origin Directory - %s', self.origin_path)
                shutil.rmtree(self.origin_path)
            self.logger.info('Removing Working Directory - %s', self.dir_path)
            shutil.rmtree(self.dir_path)
            self.logger.info('Clean Up Process Complete')

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "CLEAN_UP_ERROR: Unable to complete clean up process")

    ########################
    #   Domain Functions   #
    ########################

    def _dn2db(self, domain, add_domain=False):
        """Adds a domain to dn_db and returns the obfuscated value."""
        try:
            o_domain = self.dn_db.get(domain)
            if o_domain is None:
                # Try converting it all to lowercase
                if add_domain:
                    self.domain_count += 1
                    o_domain = "ofuscateddomain%s.com" % self.domain_count
                    self.dn_db[domain] = o_domain
                    self.logger.con_out(
                        "Adding new obfuscated domain - %s > %s", domain, o_domain)

            if o_domain:
                return o_domain
            else:
                return None

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "DN2DB_ERROR: Unable to retrieve obfuscated domain - %s", domain)

    def _domains2db(self):
        """Adds domains to the domain database"""
        try:
            # First we'll grab the domain for the sosreport and obfuscate it to the base root_domain
            # value, which defaults to "obfuscateddomain.com"
            if self.domainname is not None:
                self._dn2db(self.domainname, add_domain=True)

            for dom in self.domains:
                self._dn2db(dom, add_domain=True)

            for dom in self.short_domains:
                self._dn2db(dom, add_domain=True)

            return True

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception("DOMAINS2DB_ERROR: Unable to process domains")

    #########################
    #   Keyword functions   #
    #########################

    def _keywords2db(self):
        """Adds keywords to the keyword database"""
        try:
            if len(self.keywords_file) > 0:
                for f in self.keywords_file:
                    if os.path.isfile(f):
                        with open(f, 'r') as klist:
                            for keyword in klist.readlines():
                                keyword = keyword.rstrip()
                                if len(keyword) > 1:
                                    if self.kw_db.get(keyword) is None:  # no duplicates
                                        o_kw = "obfuscatedkeyword%s" % self.kw_count
                                        self.kw_db[keyword] = o_kw
                                        self.logger.con_out(
                                            "Added Obfuscated Keyword from Keywords File - %s > %s", keyword, o_kw)
                                        self.kw_count += 1
                                else:
                                    self.logger.con_out(
                                        "Unable to add Obfuscated Keyword - %s", keyword)
                        self.logger.con_out(
                            "Added Keyword Contents from file - %s", f)

                    else:
                        self.logger.con_out(
                            "%s does not seem to be a file. Not adding any keywords from" % f)
            if len(self.keywords) > 0:
                for kw in self.keywords:
                    if len(kw) > 1:  # no single digit keywords
                        o_kw = "obfuscatedkeyword%s" % self.kw_count
                        self.kw_db[kw] = o_kw
                        self.logger.con_out(
                            "Added obfuscated keyword - %s > %s", kw, o_kw)
                        self.kw_count += 1

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "KEYWORDS2DB_ERROR: Unable to process keyword - %s", keyword)

    def _sub_keywords(self, line):
        """Accepts a line from a file in an sosreport and obfuscates any known keyword entries on the line."""
        try:
            if self.kw_count > 0:    # we have obfuscated keywords to work with
                for keyword, o_keyword in list(self.kw_db.items()):
                    if keyword in line:
                        # insights-client modification to match partial
                        #   words like old soscleaner. original expression
                        #   is r'\b%s\b'
                        line = re.sub(r'%s' % keyword, o_keyword, line)
                        self.logger.debug(
                            "Obfuscating Keyword - %s > %s", keyword, o_keyword)

            return line

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                'SUB_KEYWORDS_ERROR: Unable to obfuscate keywords on line - %s', line)

    #########################
    #   Network Functions   #
    #########################

    def _process_route_file(self):
        """Parses the output from the route command in an sosreport to populate
        self.net_db with networks to obfuscate
        """
        try:
            route_path = os.path.join(self.dir_path, 'route')
            if os.path.exists(route_path):
                fh = open(route_path, 'r')
                self.logger.info(
                    "Found route file. Auto-adding routed networks.")
                # skip the first 2 header lines and get down to the data
                data = fh.readlines()[2:]
                for line in data:
                    x = line.split()
                    if not x[0] == '0.0.0.0':  # skip the default gateway
                        net_string = "%s/%s" % (x[0], x[2])
                        self._ip4_add_network(net_string)
                        self.logger.debug(
                            "Network Added by Auto-Route Processing.")
                fh.close()
            else:
                self.logger.info(
                    "No route file found. Unable to auto-add routed networks for this system.")
        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "PROCESS_ROUTE_FILE_ERROR: Cannot process file - %s", route_path)

    def _ip4_new_obfuscate_net(self, netmask):
        """Returns a new IPv4 Network Object to be used as an obfuscated network."""
        try:
            # this is going to get hacky
            # this will return an IPv4Address object that is 129.0.0.0
            start_point = self.default_net.broadcast + 1
            x = start_point.compressed.split('.')  # break it apart
            # calculate the new first octet
            new_octet = str(int(x[0]) + self.net_count)

            self.net_count += 1
            # a new string to create the new obfuscated network object
            new_net_string = "%s.0.0.0/%s" % (new_octet, netmask)
            if six.PY3:
                retval = IPv4Network(new_net_string)
            else:
                retval = IPv4Network(unicode(new_net_string))

            return retval

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_NEW_OBFUSCATE_NET_ERROR: Unable to create new network - %s", new_net_string)

    def _ip4_parse_network(self, network):
        """Takes the input values and return useable objects from them.
        Generates an IPv4Network object for the original network, and a string
        value for the subnet mask that is used to create the obfuscated network
        """
        try:
            if six.PY3:
                net = IPv4Network(network)
            else:
                net = IPv4Network(unicode(network))
            subnet = str(net.prefixlen)

            return net, subnet

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_PARSE_NETWORK_ERROR: Unable to parse network - %s", network)

    def _ip4_network_in_db(self, network):
        """Returns True if a network already exists in self.net_db. Is used in
        self._ip4_add_network to ensure we don't get duplicate network entries
        """
        try:
            if any(network in x for x in self.net_db):
                return True
            return False

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_NETWORK_IN_DB_ERROR: Unable to test for network in network database - %s", network)

    def _add_loopback_network(self):
        """
        Adds an entry into the needed databases to keep loopback addresses
        somewhat sane. They will be obfuscated, but within the loopback numberspace.
        So more of a shuffler than anything else.
        """
        try:
            self.logger.info(
                "Adding Entry to Network Metadata Database - 127.0.0.0")
            self.net_metadata['127.0.0.0'] = dict()
            self.net_metadata['127.0.0.0']['host_count'] = 0

            if six.PY3:
                lb_net = IPv4Network('127.0.0.0/8')
            else:
                lb_net = IPv4Network(unicode('127.0.0.0/8'))
            loopback_entry = (lb_net, lb_net)
            self.net_db.append(loopback_entry)
            self.logger.con_out("Creating Loopback Network Entry")

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "ADD_LOOPBACK_NETWORK_ERROR: Unable to create obfuscated loopback network")

    def _ip4_add_network(self, network):
        """Takes any networks specified via the command-line parameters as well
        as the routes file (if present) and creates obfuscated networks for each
        of them. This is called in self._process_route_file as well as in
        self.clean_report
        """
        try:
            net, netmask = self._ip4_parse_network(network)

            # make sure we don't have duplicates
            if not self._ip4_network_in_db(net):
                new_net = self._ip4_new_obfuscate_net(
                    netmask)    # the obfuscated network
                new_entry = (net, new_net)

                self.net_db.append(new_entry)
                self.logger.con_out(
                    "Created New Obfuscated Network - %s" % new_net.with_prefixlen)

                self.net_metadata[new_net.network_address.compressed] = dict()
                self.logger.info(
                    "Adding Entry to Network Metadata Database - %s" % new_net.with_prefixlen)
                self.net_metadata[new_net.network_address.compressed]['host_count'] = 0
            else:
                self.logger.info(
                    "Network already exists in database. Not obfuscating. - %s" % network)

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_ADD_NETWORK_ERROR: Unable to add obfuscated network - %s", network)

    def _ip4_find_network(self, ip):
        """Takes an IP address and returns back the obfuscated network it belongs to
        This is called by the _ip4_2_db function
        The value returned is a string that is the network address for the given network - IPv4Network.network.compressed
        This can be used to create a new obfuscated IP address for this value
        """
        try:
            if six.PY3:
                ip = IPv4Address(ip)    # re-cast as an IPv4 object
            else:
                ip = IPv4Address(unicode(ip))    # re-cast as an IPv4 object
            network = self.default_net.network_address
            for net in self.net_db:
                if ip in net[0]:
                    # we have a match! We'll return the proper obfuscated network
                    network = net[1].network_address

            return network

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_FIND_NETWORK_ERROR: Unable to determin obfuscated network for IP address - %s", ip)

    def _ip4_in_db(self, ip):
        """Returns True if an IP is found the the obfuscation database. Returns
        False otherwise The ip parameter is an IPv4Address object This function
        is called from within _ip4_2_db
        """
        try:
            if any(ip in x for x in self.ip_db):
                return True
            return False

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_IN_DB_ERROR: Unable to verify if IP is in database - %s", ip)

    def _ip4_2_db(self, orig_ip):
        """Adds an IP address to the IP database and returns the obfuscated
        entry, or returns the existing obfuscated IP entry.
        """
        try:
            if self._ip4_in_db(orig_ip):  # the IP exists already in the database
                # http://stackoverflow.com/a/18114565/263834
                data = dict(self.ip_db)
                # we'll pull the existing obfuscated IP from the database
                obf_ip = data[orig_ip]

                return obf_ip.compressed

            else:   # it's a new database, so we have to create a new obfuscated IP for the proper network and a new ip_db entry
                # get the network information
                net = self._ip4_find_network(orig_ip)
                self.net_metadata[net.compressed]['host_count'] += 1
                # take the network and increment the number of hosts to get to the next available IP
                if six.PY3:
                    obf_ip = IPv4Address(
                        net) + self.net_metadata[net.compressed]['host_count']
                else:
                    obf_ip = IPv4Address(
                        unicode(net)) + self.net_metadata[net.compressed]['host_count']
                self.ip_db.append((orig_ip, obf_ip))

                return obf_ip.compressed

        except Exception as e:    # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "IP4_2_DB_ERROR: unable to add IP to database - %s", orig_ip)

    def _clean_files_only(self, files):
        """Processes one or more specific files, instead of a full sosreport."""
        try:
            if not (os.path.exists(self.origin_path)):
                self.logger.info("Creating Origin Path - %s" %
                                 self.origin_path)
                # create the origin_path directory
                os.makedirs(self.origin_path)
            if not (os.path.exists(self.dir_path)):
                self.logger.info("Creating Directory Path - %s" %
                                 self.dir_path)
                os.makedirs(self.dir_path)    # create the dir_path directory
            self._add_extra_files(files)

        except OSError as e:  # pragma: no cover
            # If the file already exists
            if e.errno == errno.EEXIST:
                pass
            # If there's an IO error (disk is full)
            elif e.errno == errno.EIO:  # pragma: no cover
                self.logger.exception(e)
                self.logger.con_out(
                    "CLEAN_FILE_ERROR: Not enough disk space to complete report obfusation")
                self.logger.con_out(
                    "CLEAN_FILE_ERROR: Remove partially obfuscated report and other artifacts")
                self.logger.con_out(
                    "CLEAN_FILE_ERROR: Please remedy the disk pressure and re-run soscleaner")
                self._clean_up()
            else:   # pragma: no cover
                self.logger.exception(e)
                raise Exception(
                    "CLEAN_FILES_ONLY_ERROR: Unable to clean file from dataset - OSError")

        except Exception as e:  # pragma: no cover
            self.logger.exception(e)
            raise Exception(
                "CLEAN_FILES_ONLY_ERROR: Unable toclean files from dataset")

    def _process_report_dir(self, report_dir):  # pragma: no cover
        """Overrides the default (/tmp) location for the soscleaner run"""
        try:  # pragma: no cover
            if os.path.isdir(report_dir):
                self.report_dir = report_dir

            return True

        except Exception as e:
            self.logger.exception(e)
            raise Exception(
                "PROCESS_REPORT_DIR_ERROR: Unable to set report output directory")

    def _start_soscleaner(self):  # pragma no cover
        """Sets up the data structures and filesystem attributes to get soscleaner going properly"""
        try:
            self.origin_path, self.dir_path, self.session, self.logfile, self.uuid = self._prep_environment()
            self._start_logging(self.logfile)
            self._check_uid()  # make sure it's soscleaner is running as root
            self._get_version()
            self._get_disclaimer()
        except Exception as e:
            self.logger.exception(e)
            raise Exception(
                "START_SOSCLEANER_ERROR: Unable to create needed artifacts to run soscleaner")

    def clean_report(self, options, sosreport):  # pragma: no cover
        """The primary function, to put everything together and analyze an sosreport."""
        if options.report_dir:
            self._process_report_dir(options.report_dir)
        self.loglevel = options.loglevel
        self._start_soscleaner()
        self._read_later_config_options()
        if options.obfuscate_macs:
            self.obfuscate_macs = options.obfuscate_macs
        self._add_loopback_network()
        if options.networks:    # we have defined networks
            self.networks = options.networks
            for network in options.networks:
                self._ip4_add_network(network)
        if options.domains:
            self.domains.extend(options.domains)
        if options.keywords_file:
            self.keywords_file = options.keywords_file
        if options.keywords:
            self.keywords = options.keywords
        self._keywords2db()
        if options.users:  # users from the command line with the -u option
            self._process_user_option(options.users)
        if options.users_file:
            self.users_file = options.users_file
        if not sosreport:
            if not options.files:
                raise Exception(
                    "Error: You must supply either an sosreport and/or files to process")
            self.logger.con_out(
                "No sosreport supplied. Only processing specific files")
            if not options.networks:
                self.logger.con_out(
                    "No sosreport supplied and no networks specified. All IP addresses will be obfuscated into the same default subnet")
            self._clean_files_only(options.files)

        else:   # we DO have an sosreport to analyze
            self.report = self._extract_sosreport(sosreport)
            self._make_dest_env()   # create the working directory
            if options.hostname_path:
                self.hostname, self.domainname = self._get_hostname(
                    options.hostname_path)
            else:
                self.hostname, self.domainname = self._get_hostname()
            self._process_route_file()
            if options.files:
                self._add_extra_files(options.files)
            if self.hostname:   # if we have a hostname that's not a None type
                # we'll prime the hostname pump to clear out a ton of useless logic later
                self.hn_db['host0'] = self.hostname

        self._domains2db()
        files = self._file_list(self.dir_path)
        self._process_users_file()
        self.logger.con_out(
            "IP Obfuscation Network Created - %s", self.default_net.compressed)
        self.logger.con_out("*** SOSCleaner Processing ***")
        self.logger.info("Working Directory - %s", self.dir_path)
        for f in files:
            self.logger.debug("Cleaning %s", f)
            self._clean_file(f)
        self.logger.con_out("*** SOSCleaner Statistics ***")
        self.logger.con_out("IP Addresses Obfuscated - %s", len(self.ip_db))
        self.logger.con_out("Hostnames Obfuscated - %s", len(self.hn_db))
        self.logger.con_out("Domains Obfuscated - %s", len(self.dn_db))
        self.logger.con_out("Users Obfuscated - %s", self.user_count)
        self.logger.con_out("Keywords Obfuscated - %s", self.kw_count)
        self.logger.con_out("Total Files Analyzed - %s", self.file_count)
        self.logger.con_out("*** SOSCleaner Artifacts ***")
        self._create_reports()

        # This if-block added for insights-client --output-dir option.
        #   Prevent calling of _create_archive() so that dir_path is
        #   not removed and archive is not unnecessarily created.
        #   Furthermore, the client does not utilize soscleaner return
        #   data, so return here. Further code beyond the block
        #   is left as-is.
        if options.no_tar_file:
            return
        # end insights-client modifications

        self._create_archive()
        self.soscleaner_checksum()
        self.finalmsg()

        return_data = [self.archive_path, self.logfile, self.ip_report]

        if self.hostname:
            return_data.append(self.hn_report)
        if len(self.dn_db) >= 1:
            return_data.append(self.dn_report)

        return return_data
