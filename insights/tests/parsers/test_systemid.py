from insights.tests import context_wrap
from insights.parsers.systemid import SystemID

SYSTEMID = '''
<?xml version="1.0"?>
<params>
<param>
<value><struct>
<member>
<name>username</name>
<value><string>testuser</string></value>
</member>
<member>
<name>operating_system</name>
<value><string>redhat-release-workstation</string></value>
</member>
<member>
<name>description</name>
<value><string>Initial Registration Parameters: OS: redhat-release-workstation Release: 6Workstation CPU Arch: x86_64</string></value>
</member>
<member>
<name>checksum</name>
<value><string>b493da72be7cfb7e54c1d58c6aa140c9</string></value>
</member>
<member>
<name>profile_name</name>
<value><string>example_profile</string></value>
</member>
<member>
<name>system_id</name>
<value><string>ID-example</string></value>
</member>
<member>
<name>architecture</name>
<value><string>x86_64</string></value>
</member>
<member>
<name>os_release</name>
<value><string>6Workstation</string></value>
</member>
<member>
<name>fields</name>
<value><array><data>
<value><string>system_id</string></value>
<value><string>os_release</string></value>
<value><string>operating_system</string></value>
<value><string>architecture</string></value>
<value><string>username</string></value>
<value><string>type</string></value>
</data></array></value>
</member>
<member>
<name>type</name>
<value><string>REAL</string></value>
</member>
</struct></value>
</param>
</params>
'''.strip()


def test_systemid():
    info = SystemID(context_wrap(SYSTEMID, path='/etc/sysconfig/rhn/systemid'))

    assert info.get("username") == 'testuser'
    assert info.get("operating_system") == 'redhat-release-workstation'
    assert info.get("description") == 'Initial Registration Parameters: OS: redhat-release-workstation Release: 6Workstation CPU Arch: x86_64'
    assert info.get("checksum") == 'b493da72be7cfb7e54c1d58c6aa140c9'
    assert info.get("profile_name") == 'example_profile'
    assert info.get("system_id") == 'ID-example'
    assert info.get("architecture") == 'x86_64'
    assert info.get("os_release") == '6Workstation'
    assert info.get("type") == 'REAL'

    assert info.file_name == 'systemid'
    assert info.file_path == '/etc/sysconfig/rhn/systemid'
