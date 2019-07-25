import doctest
from insights.combiners import dnf_module_info
from insights.combiners.dnf_module_info import DnfModuleInfoAll
from insights.parsers.dnf_module import DnfModuleInfo
from insights.tests import context_wrap

DNF_MODULE_INFO1 = """
Updating Subscription Management repositories.
Last metadata expiration check: 0:01:39 ago on Thu 25 Jul 2019 01:32:41 PM CST.
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

Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled, [a]ctive]
""".strip()

DNF_MODULE_INFO2 = """
Updating Subscription Management repositories.
Last metadata expiration check: 0:02:09 ago on Thu 25 Jul 2019 01:32:41 PM CST.
Name             : httpd
Stream           : 2.4 [d][e][a]
Version          : 8000020190405071959
Context          : 55190bc5
Profiles         : common [d] [i], devel, minimal
Default profiles : common
Repo             : rhel-8-for-x86_64-appstream-rpms
Summary          : Apache HTTP Server
Description      : Apache httpd is a powerful, efficient, and extensible HTTP server.
Artifacts        : httpd-0:2.4.37-11.module+el8.0.0+2969+90015743.src
                 : httpd-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : httpd-debuginfo-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : httpd-debugsource-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : httpd-devel-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : httpd-filesystem-0:2.4.37-11.module+el8.0.0+2969+90015743.noarch
                 : httpd-manual-0:2.4.37-11.module+el8.0.0+2969+90015743.noarch
                 : httpd-tools-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : httpd-tools-debuginfo-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_http2-0:1.11.3-2.module+el8.0.0+2969+90015743.src
                 : mod_http2-0:1.11.3-2.module+el8.0.0+2969+90015743.x86_64
                 : mod_http2-debuginfo-0:1.11.3-2.module+el8.0.0+2969+90015743.x86_64
                 : mod_http2-debugsource-0:1.11.3-2.module+el8.0.0+2969+90015743.x86_64
                 : mod_ldap-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_ldap-debuginfo-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_md-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_md-debuginfo-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_proxy_html-1:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_proxy_html-debuginfo-1:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_session-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_session-debuginfo-0:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_ssl-1:2.4.37-11.module+el8.0.0+2969+90015743.x86_64
                 : mod_ssl-debuginfo-1:2.4.37-11.module+el8.0.0+2969+90015743.x86_64

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
""".strip()

DNF_MODULE_INFO3 = """
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

Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled, [a]ctive]
""".strip()


def test_dnf_module_info_all():
    module_info1 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO1))
    module_info2 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO2))
    module_info3 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO3))
    mod_all = DnfModuleInfoAll([module_info1, module_info2, module_info3])
    assert 'ant' in mod_all
    assert mod_all['httpd'][0].name == 'httpd'
    assert mod_all['httpd'][0].stream == '2.4 [d][e][a]'


def test_dnf_module_info_doc_examples():
    module_info1 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO1))
    module_info2 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO2))
    module_info3 = DnfModuleInfo(context_wrap(DNF_MODULE_INFO3))
    env = {
        'all_mods': DnfModuleInfoAll([module_info1, module_info2, module_info3])
    }
    failed, total = doctest.testmod(dnf_module_info, globs=env)
    assert failed == 0
