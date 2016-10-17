from falafel.mappers import samba
from falafel.tests import context_wrap

SAMBA_CONFIG = """
# This is the main Samba configuration file. You should read the
# smb.conf(5) manual page in order to understand the options listed
#...
#======================= Global Settings =====================================
	
[global]
	
#...
# Hosts Allow/Hosts Deny lets you restrict who can connect, and you can
# specifiy it as a per share option as well
#
	workgroup = MYGROUP
	server string = Samba Server Version %v
	
;	netbios name = MYSERVER
	
;	interfaces = lo eth0 192.168.12.2/24 192.168.13.2/24 
;	hosts allow = 127. 192.168.12. 192.168.13.
	
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

;	printcap name = /etc/printcap
	#obtain list of printers automatically on SystemV
;	printcap name = lpstat
;	printing = cups

# --------------------------- Filesystem Options ---------------------------
#
# The following options can be uncommented if the filesystem supports
# Extended Attributes and they are enabled (usually by the mount option
# user_xattr). Thess options will let the admin store the DOS attributes
# in an EA and make samba not mess with the permission bits.
#
# Note: these options can also be set just per share, setting them in global
# makes them the default for all shares

;	map archive = no
;	map hidden = no
;	map read only = no
;	map system = no
;	store dos attributes = yes


#============================ Share Definitions ==============================
	
[homes]
	comment = Home Directories
	browseable = no
	writable = yes
;	valid users = %S
;	valid users = MYDOMAIN\%S
	
[printers]
	comment = All Printers
	path = /var/spool/samba
	browseable = no
	guest ok = no
	writable = no
	printable = yes
	
# Un-comment the following and create the netlogon directory for Domain Logons
;	[netlogon]
;	comment = Network Logon Service
;	path = /var/lib/samba/netlogon
;	guest ok = yes
;	writable = no
;	share modes = no
	
	
# Un-comment the following to provide a specific roving profile share
# the default is to use the user's home directory
;	[Profiles]
;	path = /var/lib/samba/profiles
;	browseable = no
;	guest ok = yes
	
	
# A publicly accessible directory, but read only, except for people in
# the "staff" group
;	[public]
;	comment = Public Stuff
;	path = /home/samba
;	public = yes
;	writable = yes
;	printable = no
;	write list = +staff
"""

def test_match():
    config = samba.SambaConfig(context_wrap(SAMBA_CONFIG))

    assert isinstance(config.get('global'), dict) 
    assert config.get('global').get('workgroup') == 'MYGROUP'
    assert config.get_key('global', 'workgroup') == 'MYGROUP'
    assert config.get_key('global', 'server string') == 'Samba Server Version %v'
    assert config.get_key('global', 'netbios name') is None
    assert config.get_key('global', 'log file') == '/var/log/samba/log.%m'
    assert config.get_key('global', 'max log size') == '50'

    assert config.get_key('global', 'security') == 'user'
    assert config.get_key('global', 'passdb backend') == 'tdbsam'

    assert config.get_key('global', 'load printers') == 'yes'
    assert config.get_key('global', 'cups options') == 'raw'

    assert config.get_key('global', 'printcap name') is None

    assert isinstance(config.get('homes'), dict) 
    assert config.get_key('homes', 'comment') == 'Home Directories'
    assert config.get_key('homes', 'browseable') == 'no'
    assert config.get_key('homes', 'writable') == 'yes'
    assert config.get_key('homes', 'valid users') is None

    assert isinstance(config.get('printers'), dict) 
    assert config.get_key('printers', 'comment') == 'All Printers'
    assert config.get_key('printers', 'path') == '/var/spool/samba'
    assert config.get_key('printers', 'browseable') == 'no'
    assert config.get_key('printers', 'guest ok') == 'no'
    assert config.get_key('printers', 'writable') == 'no'
    assert config.get_key('printers', 'printable') == 'yes'

    assert config.get('netlogon') is None
    assert config.get('Profiles') is None
    assert config.get('public') is None
