from insights.parsers.sysconfig import Up2DateSysconfig
from insights.tests import context_wrap


UP2DATE = '''
# Automatically generated Red Hat Update Agent config file, do not edit.
# Format: 1.0
retrieveOnly[comment]=Retrieve packages only
retrieveOnly=0

#noSSLServerURL[comment]=''
#noSSLServerURL=http://192.168.160.23/XMLRPC

writeChangesToLog[comment]=Log to /var/log/up2date which packages has been added and removed
writeChangesToLog=0

stagingContentWindow[comment]=How much forward we should look for future actions. In hours.
stagingContentWindow=24

networkRetries[comment]=Number of attempts to make at network connections before giving up
networkRetries=5

enableProxy[comment]=Use a HTTP Proxy
enableProxy=0

proxyPassword[comment]=The password to use for an authenticated proxy
proxyPassword=

*** of system id
systemIdPath=/etc/sysconfig/rhn/systemid

useNoSSLForPackages[comment]=Use the noSSLServerURL for package, package list, and header fetching (disable Akamai)
useNoSSLForPackages=0

tmpDir[comment]=Use this Directory to place the temporary transport files
tmpDir=/tmp

#serverURL[comment]=Remote server URL
#serverURL=http://192.168.160.23/XMLRPC

skipNetwork[comment]=Skips network information in hardware profile sync during registration.
skipNetwork=0

disallowConfChanges[comment]=Config options that can not be overwritten by a config update action
disallowConfChanges=noReboot;sslCACert;useNoSSLForPackages;noSSLServerURL;serverURL;disallowConfChanges;

#sslCACert[comment]=The CA cert used to verify the ssl server
#sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT

enableProxyAuth[comment]=To use an authenticated proxy or not
enableProxyAuth=0

versionOverride[comment]=Override the automatically determined system version
versionOverride=

stagingContent[comment]=Retrieve content of future actions in advance
stagingContent=1

proxyUser[comment]=The username for an authenticated proxy
proxyUser=

hostedWhitelist[comment]=RHN Hosted URL's
hostedWhitelist=

debug[comment]=Whether or not debugging is enabled
debug=0

httpProxy[comment]=HTTP proxy in host:port format, e.g. squid.redhat.com:3128
httpProxy=

noReboot[comment]=Disable the reboot actions
noReboot=0

#serverURL=http://192.168.160.23/XMLRPC
#noSSLServerURL=http://192.168.160.23/XMLRPC
#sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
serverURL=http://192.168.160.23/XMLRPC
noSSLServerURL=http://192.168.160.23/XMLRPC
sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
'''


def test_get_up2date():
    up2date_info = Up2DateSysconfig(context_wrap(UP2DATE)).data

    assert up2date_info['retrieveOnly'] == '0'
    assert up2date_info['writeChangesToLog'] == '0'
    assert up2date_info['stagingContentWindow'] == '24'
    assert up2date_info['networkRetries'] == '5'
    assert up2date_info['enableProxy'] == '0'
    assert up2date_info['proxyPassword'] == ''
    assert up2date_info['systemIdPath'] == '/etc/sysconfig/rhn/systemid'
    assert up2date_info['useNoSSLForPackages'] == '0'
    assert up2date_info['tmpDir'] == '/tmp'
    assert up2date_info['skipNetwork'] == '0'
    assert up2date_info['disallowConfChanges'] == 'noReboot;sslCACert;useNoSSLForPackages;noSSLServerURL;serverURL;disallowConfChanges;'
    assert up2date_info['enableProxyAuth'] == '0'
    assert up2date_info['versionOverride'] == ''
    assert up2date_info['stagingContent'] == '1'
    assert up2date_info['proxyUser'] == ''
    assert up2date_info['hostedWhitelist'] == ''
    assert up2date_info['debug'] == '0'
    assert up2date_info['httpProxy'] == ''
    assert up2date_info['noReboot'] == '0'
    assert up2date_info['serverURL'] == 'http://192.168.160.23/XMLRPC'
    assert up2date_info['noSSLServerURL'] == 'http://192.168.160.23/XMLRPC'
    assert up2date_info['sslCACert'] == '/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT'
