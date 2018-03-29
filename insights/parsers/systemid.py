from .. import XMLParser, parser
from insights.specs import Specs


@parser(Specs.systemid)
class SystemID(XMLParser):
    '''
    ---------------
    Return a SystemId object which contains a dict below:
        {
        "username": "testuser",
        "operating_system": "redhat-release-workstation",
        "description": "Initial Registration Parameters: OS: redhat-release-workstation Release: 6Workstation CPU Arch: x86_64",
        "checksum": "b493da72be7cfb7e54c1d58c6aa140c9",
        "profile_name": "example_profile",
        "system_id": "ID-example",
        "architecture": "x86_64",
        "os_release": "6Workstation",
        "type": "REAL"
        }
    Ignore the member with "fields" text. Because it's information is nonsense
    ---Sample---
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
    <value><string>Initial Registration Parameters:
    OS: redhat-release-workstation
    Release: 6Workstation
    CPU Arch: x86_64</string></value>
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
    '''

    def parse_dom(self):
        systemid_info = {}

        for member in self.dom.findall(".//member"):
            # ignore "fields" infos
            if member[0].text != 'fields':
                key = member[0].text
                value = member[1][0].text
                systemid_info[key] = value
        return systemid_info
