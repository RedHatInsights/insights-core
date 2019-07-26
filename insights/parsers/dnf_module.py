"""
dnf module commands
===================

Parsers provided in this module includes:

DnfModuleList - command ``dnf module list``
-------------------------------------------

DnfModuleInfo - command ``dnf module info *``
---------------------------------------------
"""
from insights import parser
from insights.core import CommandParser
from insights.parsers import parse_fixed_table, SkipException
from insights.specs import Specs


class DnfModuleBrief(object):
    """
    An object for the dnf modules listed by ``dnf module list`` command

    Attributes:
        name (str): Name of the dnf module
        stream (str): Stream of the dnf module
        profiles (list): List of profiles of the dnf module
        summary (str): Summary of the dnf module
    """
    def __init__(self, data=None):
        data = {} if data is None else data
        self.name = data.get('Name', '')
        self.stream = data.get('Stream', '')
        self.profiles = list(filter(None, [i.strip() for i in data.get('Profiles', '').split(',')]))
        self.summary = data.get('Summary', '')


class DnfModuleDetail(DnfModuleBrief):
    """
    An object for the dnf modules listed by ``dnf module info`` command

    Attributes:
        name (str): Name of the dnf module
        stream (str): Stream of the dnf module
        version (str): Version of the dnf module
        context (str): Context of the dnf module
        profiles (list): List of profiles of the dnf module
        default_profiles (str): Default profile of the dnf module
        repo (str): Repo of the dnf module
        summary (str): Summary of the dnf module
        description (str): Description of the dnf module
        artifacts (list): List of the artifacts of the dnf module
    """
    def __init__(self, data=None):
        super(DnfModuleDetail, self).__init__(data)
        self.version = data.get('Version', '')
        self.context = data.get('Context', '')
        self.default_profiles = data.get('Default profiles', '')
        self.repo = data.get('Repo', '')
        self.description = data.get('Description', '')
        self.artifacts = data.get('Artifacts', '').split()


@parser(Specs.dnf_module_list)
class DnfModuleList(CommandParser, dict):
    """
    Class to parse the output of command `dnf module list`
    Typical output of the command is::

        Updating Subscription Management repositories.
        Name                Stream      Profiles                                  Summary
        389-ds              1.4                                                   389 Directory Server (base)
        ant                 1.10 [d]    common [d]                                Java build tool

        Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled

    Examples:
        >>> len(dnf_module_list)
        2
        >>> dnf_module_list.get("389-ds").stream
        '1.4'
        >>> dnf_module_list.get("389-ds").profiles
        []
        >>> dnf_module_list.get("ant").stream
        '1.10 [d]'
    """
    def __init__(self, *args, **kwargs):
        super(DnfModuleList, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        data = parse_fixed_table(content,
                        heading_ignore=['Name '],
                        trailing_ignore=['Hint:', 'Error:'])
        if not data:
            raise SkipException('Nothing need to parse.')
        for m in data:
            self.update({m['Name']: DnfModuleBrief(m)})

    @property
    def modules(self):
        """Returns a list of modules name"""
        return sorted(self.keys())


@parser(Specs.dnf_module_info)
class DnfModuleInfo(CommandParser, dict):
    """
    Class to parse the output of command `dnf module info XX, YY`

    Typical output of the command is::

        Updating Subscription Management repositories.
        Last metadata expiration check: 0:31:25 ago on Thu 25 Jul 2019 12:19:22 PM CST.
        Name        : 389-ds
        Stream      : 1.4
        Version     : 8000020190424152135
        Context     : ab753183
        Repo        : rhel-8-for-x86_64-appstream-rpms
        Summary     : 389 Directory Server (base)
        Description : 389 Directory Server is an LDAPv3 compliant server.  The base package includes the LDAP server and command line utilities for server administration.
        Artifacts   : 389-ds-base-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.src
                    : 389-ds-base-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-debuginfo-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-debugsource-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-devel-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-legacy-tools-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-legacy-tools-debuginfo-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-libs-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-libs-debuginfo-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-snmp-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : 389-ds-base-snmp-debuginfo-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.x86_64
                    : python3-lib389-0:1.4.0.20-10.module+el8.0.0+3096+101825d5.noarch

        Name        : 389-ds
        Stream      : 1.4
        Version     : 820190201170147
        Context     : 1fc8b219
        Repo        : rhel-8-for-x86_64-appstream-rpms
        Summary     : 389 Directory Server (base)
        Description : 389 Directory Server is an LDAPv3 compliant server.  The base package includes the LDAP server and command line utilities for server administration.
        Artifacts   : 389-ds-base-0:1.4.0.20-7.module+el8+2750+1f4079fb.x86_64
                    : 389-ds-base-devel-0:1.4.0.20-7.module+el8+2750+1f4079fb.x86_64
                    : 389-ds-base-legacy-tools-0:1.4.0.20-7.module+el8+2750+1f4079fb.x86_64
                    : 389-ds-base-libs-0:1.4.0.20-7.module+el8+2750+1f4079fb.x86_64
                    : 389-ds-base-snmp-0:1.4.0.20-7.module+el8+2750+1f4079fb.x86_64
                    : python3-lib389-0:1.4.0.20-7.module+el8+2750+1f4079fb.noarch

        Name             : ant
        Stream           : 1.10 [d][a]
        Version          : 820181213135032
        Context          : 5ea3b708
        Profiles         : common [d]
        Default profiles : common
        Repo             : rhel-8-for-x86_64-appstream-rpms
        Summary          : Java build tool
        Description      : Apache Ant is a Java library and command-line tool whose mission is to drive processes described in build files as targets and extension points dependent upon each other. The main known usage of Ant is the build of Java applications. Ant supplies a number of built-in tasks allowing to compile, assemble, test and run Java applications. Ant can also be used effectively to build non Java applications, for instance C or C++ applications. More generally, Ant can be used to pilot any type of process which can be described in terms of targets and tasks.
        Artifacts        : ant-0:1.10.5-1.module+el8+2438+c99a8a1e.noarch
                         : ant-lib-0:1.10.5-1.module+el8+2438+c99a8a1e.noarch

        Name             : httpd
        Stream           : 2.4 [d][e][a]
        Version          : 820190206142837
        Context          : 9edba152
        Profiles         : common [d] [i], devel, minimal
        Default profiles : common
        Repo             : rhel-8-for-x86_64-appstream-rpms
        Summary          : Apache HTTP Server
        Description      : Apache httpd is a powerful, efficient, and extensible HTTP server.
        Artifacts        : httpd-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : httpd-devel-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : httpd-filesystem-0:2.4.37-10.module+el8+2764+7127e69e.noarch
                         : httpd-manual-0:2.4.37-10.module+el8+2764+7127e69e.noarch
                         : httpd-tools-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : mod_http2-0:1.11.3-1.module+el8+2443+605475b7.x86_64
                         : mod_ldap-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : mod_md-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : mod_proxy_html-1:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : mod_session-0:2.4.37-10.module+el8+2764+7127e69e.x86_64
                         : mod_ssl-1:2.4.37-10.module+el8+2764+7127e69e.x86_64

        Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled, [a]ctive]

    The modules information is wrapped in this object like a dictionary, with
    the module name as the key and the list of the :class:`DnfModuleDetail` as
    the value.

    Examples:
        >>> type(dnf_module_info)
        <class 'insights.parsers.dnf_module.DnfModuleInfo'>
        >>> len(dnf_module_info)
        3
        >>> dnf_module_info.modules
        ['389-ds', 'ant', 'httpd']
        >>> "389-ds" in dnf_module_info
        True
        >>> len(dnf_module_info.get("389-ds"))
        2
        >>> type(dnf_module_info.get("389-ds")[0])
        <class 'insights.parsers.dnf_module.DnfModuleDetail'>
        >>> dnf_module_info['389-ds'][0].name
        '389-ds'
        >>> dnf_module_info["389-ds"][0].profiles
        []
        >>> dnf_module_info["389-ds"][0].default_profiles
        ''
        >>> dnf_module_info['389-ds'][1].name
        '389-ds'
        >>> dnf_module_info['389-ds'][1].context
        '1fc8b219'
        >>> "ant" in dnf_module_info
        True
        >>> len(dnf_module_info.get("ant"))
        1
        >>> type(dnf_module_info.get("ant")[0])
        <class 'insights.parsers.dnf_module.DnfModuleDetail'>
        >>> dnf_module_info['ant'][0].name
        'ant'
        >>> dnf_module_info['ant'][0].context
        '5ea3b708'
        >>> dnf_module_info["ant"][0].version
        '820181213135032'
        >>> dnf_module_info['ant'][0].profiles
        ['common [d]']
        >>> dnf_module_info['ant'][0].default_profiles
        'common'
        >>> dnf_module_info["httpd"][0].profiles
        ['common [d] [i]', 'devel', 'minimal']
        >>> dnf_module_info["httpd"][0].default_profiles
        'common'
    """
    def __init__(self, *args, **kwargs):
        super(DnfModuleInfo, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        def _update_value(k, v):
            if k not in self:
                self[k] = []
            self[k].append(v)

        mod_dict = {}
        key_prev = ''
        for line in content:
            if " : " in line:
                k, v = [s.strip() for s in line.split(' : ', 1)]
                k = key_prev if not k and key_prev else k
                if k in mod_dict:
                    mod_dict[k] = '{0}\r{1}'.format(mod_dict[k], v)
                else:
                    mod_dict[k] = v
                key_prev = k
            elif not line.strip() and mod_dict:
                mod_info = DnfModuleDetail(mod_dict)
                _update_value(mod_info.name, mod_info)
                mod_dict = {}

        if mod_dict:
            mod_info = DnfModuleDetail(mod_dict)
            _update_value(mod_info.name, mod_info)

        if self.__len__() == 0:
            raise SkipException('Nothing need to parse.')

    @property
    def modules(self):
        """Returns a list of modules name"""
        return sorted(self.keys())
