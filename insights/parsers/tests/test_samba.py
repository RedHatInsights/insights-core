import pytest

from insights.parsers import samba, ParseException
from insights.tests import context_wrap
from doctest import testmod

SAMBA_CONFIG_DOCUMENTATION = '''
# This is the main Samba configuration file. You should read the
# smb.conf(5) manual page in order to understand the options listed
#...
#======================= Global Settings =====================================

[global]
    workgroup = MYGROUP
    server string = Samba Server Version %v
    max log size = 50

[homes]
    comment = Home Directories
    browseable = no
    writable = yes
;   valid users = %S
;   valid users = MYDOMAIN\%S

[printers]
    comment = All Printers
    path = /var/spool/samba
    browseable = no
    guest ok = no
    writable = no
    printable = yes

# A publicly accessible directory, but read only, except for people in
# the "staff" group
[public]
   comment = Public Stuff
   path = /home/samba
   public = yes
   writable = yes
   printable = no
   write list = +staff
'''


def test_documentation():
    failed, total = testmod(samba, globs={
        'conf': samba.SambaConfig(context_wrap(SAMBA_CONFIG_DOCUMENTATION)),
    })
    assert failed == 0


SAMBA_CONFIG = """
# This is the main Samba configuration file. You should read the
# smb.conf(5) manual page in order to understand the options listed
#...
#======================= Global Settings =====================================

# By running `testparm`, it is apparent that options outside the [global]
# section before the [global] section are treated as if they were in the
# [global] section.
# `testparm` is a program from the samba package.

this option should be in global = yes

[global]

#...
# Hosts Allow/Hosts Deny lets you restrict who can connect, and you can
# specifiy it as a per share option as well
#
    workgroup = MYGROUP
    server string = Samba Server Version %v

;   netbios name = MYSERVER

;   interfaces = lo eth0 192.168.12.2/24 192.168.13.2/24
;   hosts allow = 127. 192.168.12. 192.168.13.

# --------------------------- Logging Options -----------------------------
#
# Log File let you specify where to put logs and how to split them up.
#
# Max Log Size let you specify the max size log files should reach

    # logs split per machine
    log file = /var/log/samba/log.%m
    # max 50KB per log file, then rotate
    max log size = 50

# ----------------------- Standalone Server Options ------------------------
#
# Scurity can be set to user, share(deprecated) or server(deprecated)
#
# Backend to store user information in. New installations should
# use either tdbsam or ldapsam. smbpasswd is available for backwards
# compatibility. tdbsam requires no further configuration.

    security = user
    passdb backend = tdbsam

#...
# --------------------------- Printing Options -----------------------------
#
# Load Printers let you load automatically the list of printers rather
# than setting them up individually
#
# Cups Options let you pass the cups libs custom options, setting it to raw
# for example will let you use drivers on your Windows clients
#
# Printcap Name let you specify an alternative printcap file
#
# You can choose a non default printing system using the Printing option

    load printers = yes
    cups options = raw

;   printcap name = /etc/printcap
    #obtain list of printers automatically on SystemV
;   printcap name = lpstat
;   printing = cups

# --------------------------- Filesystem Options ---------------------------
#
# The following options can be uncommented if the filesystem supports
# Extended Attributes and they are enabled (usually by the mount option
# user_xattr). Thess options will let the admin store the DOS attributes
# in an EA and make samba not mess with the permission bits.
#
# Note: these options can also be set just per share, setting them in global
# makes them the default for all shares

;   map archive = no
;   map hidden = no
;   map read only = no
;   map system = no
;   store dos attributes = yes


#============================ Share Definitions ==============================

[homes]
    comment = Home Directories
    browseable = no
    writable = yes
;   valid users = %S
;   valid users = MYDOMAIN\%S

[printers]
    comment = All Printers
    path = /var/spool/samba
    browseable = no
    guest ok = no
    writable = no
    printable = yes

# Un-comment the following and create the netlogon directory for Domain Logons
;   [netlogon]
;   comment = Network Logon Service
;   path = /var/lib/samba/netlogon
;   guest ok = yes
;   writable = no
;   share modes = no


# Un-comment the following to provide a specific roving profile share
# the default is to use the user's home directory
;   [Profiles]
;   path = /var/lib/samba/profiles
;   browseable = no
;   guest ok = yes


# A publicly accessible directory, but read only, except for people in
# the "staff" group
;   [public]
;   comment = Public Stuff
;   path = /home/samba
;   public = yes
;   writable = yes
;   printable = no
;   write list = +staff

[ GlObAl  ]

# Samba also automatically treats non-lowercase section names as lowercase and strips whitespace.
# This behavior can be checked with `testparm` again.
this option should also be in global = true

[ GlObAl  ]

# This tests specifically that two same-named sections are automatically merged in case the
# RawConfigParser's behavior ever changes.
this another option should also be in global = 1
"""

# This is going to be filtered, so removing following lines:
#
# Load smb config files from /etc/samba/smb.conf
# Loaded services file OK.

TESTPARM = """
Server role: ROLE_STANDALONE

# Global parameters
[global]
	add user to group script = 
	afs token lifetime = 604800
	afs username map = 
	aio max threads = 100
	server schannel = Yes

[homes]
	browseable = No

"""  # noqa: E101,W191,W291


def test_match():
    for config in [samba.SambaConfig(context_wrap(SAMBA_CONFIG)),  # noqa: E101
                   samba.SambaConfigs(context_wrap("Server role: ROLE_STANDALONE\n\n" +
                                      SAMBA_CONFIG)),
                   samba.SambaConfigsAll(context_wrap("Server role: ROLE_STANDALONE\n\n" +
                                      SAMBA_CONFIG)),
                   ]:
        assert config.get('global', 'this option should be in global') == 'yes'
        assert config.get('global', 'this option should also be in global') == 'true'
        assert config.get('global', 'this another option should also be in global') == '1'
        assert config.get('global', 'workgroup') == 'MYGROUP'
        assert config.get('global', 'workgroup') == 'MYGROUP'
        assert config.get('global', 'server string') == 'Samba Server Version %v'
        assert not config.has_option('global', 'netbios name')
        assert config.get('global', 'log file') == '/var/log/samba/log.%m'
        assert config.get('global', 'max log size') == '50'

        assert config.get('global', 'security') == 'user'
        assert config.get('global', 'passdb backend') == 'tdbsam'

        assert config.get('global', 'load printers') == 'yes'
        assert config.get('global', 'cups options') == 'raw'

        assert not config.has_option('global', 'printcap name')

        assert config.get('homes', 'comment') == 'Home Directories'
        assert config.get('homes', 'browseable') == 'no'
        assert config.get('homes', 'writable') == 'yes'
        assert not config.has_option('homes', 'valid users')

        assert config.get('printers', 'comment') == 'All Printers'
        assert config.get('printers', 'path') == '/var/spool/samba'
        assert config.get('printers', 'browseable') == 'no'
        assert config.get('printers', 'guest ok') == 'no'
        assert config.get('printers', 'writable') == 'no'
        assert config.get('printers', 'printable') == 'yes'

        assert 'netlogin' not in config
        assert 'Profiles' not in config
        assert 'public' not in config


def test_server_role():
    config = samba.SambaConfigs(context_wrap(TESTPARM))

    assert config.get('global', 'server schannel') == 'Yes'
    assert config.get('homes', 'browseable') == 'No'
    assert config.get('global', 'afs username map') == ''
    assert config.server_role == "ROLE_STANDALONE"


def test_server_role_missing():
    with pytest.raises(ParseException) as e:
        samba.SambaConfigs(context_wrap(SAMBA_CONFIG))
        assert e.value == "Server role not found."
