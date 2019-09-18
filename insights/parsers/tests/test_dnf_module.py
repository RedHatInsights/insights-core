import doctest
import pytest
from insights.parsers import dnf_module, SkipException
from insights.parsers.dnf_module import DnfModuleList, DnfModuleInfo
from insights.tests import context_wrap

DNF_MODULE_LIST = """
Updating Subscription Management repositories.
Red Hat Enterprise Linux 8 for x86_64 - AppStream (RPMs)                  1.9 kB/s | 4.5 kB     00:02
Red Hat Enterprise Linux 8 for x86_64 - BaseOS (RPMs)                     1.7 kB/s | 4.0 kB     00:02
Red Hat Enterprise Linux 8 for x86_64 - Supplementary (RPMs)              1.6 kB/s | 3.8 kB     00:02
Red Hat Enterprise Linux 8 for x86_64 - AppStream (RPMs)
Name                Stream      Profiles                                  Summary
389-ds              1.4                                                   389 Directory Server (base)
ant                 1.10 [d]    common [d]                                Java build tool
container-tools     1.0         common [d]                                Common tools and dependencies for container runtimes
container-tools     rhel8 [d]   common [d]                                Common tools and dependencies for container runtimes
freeradius          3.0 [d]     server [d]                                High-performance and highly configurable free RADIUS server
gimp                2.8 [d]     common [d], devel                         gimp module
go-toolset          rhel8 [d]   common [d]                                Go
httpd               2.4 [d][e]  common [d] [i], devel, minimal            Apache HTTP Server
idm                 DL1         common [d], adtrust, client, dns, server  The Red Hat Enterprise Linux Identity Management system module
pki-core            10.6                                                  PKI Core
pki-deps            10.6                                                  PKI Dependencies module
postgresql          10 [d]      client, server [d]                        PostgreSQL server and client module
postgresql          9.6         client, server [d]                        PostgreSQL server and client module
python27            2.7 [d]     common [d]                                Python programming language, version 2.7
python36            3.6 [d][e]  common [d], build                         Python programming language, version 3.6
redis               5 [d]       common [d]                                Redis persistent key-value database
rhn-tools           1.0 [d]     common [d]                                Red Hat Satellite 5 tools for RHEL
ruby                2.5 [d]     common [d]                                An interpreter of object-oriented scripting language
rust-toolset        rhel8 [d]   common [d]                                Rust
satellite-5-client  1.0 [d]     common [d], gui                           Red Hat Satellite 5 client packages
scala               2.10 [d]    common [d]                                A hybrid functional/object-oriented language for the JVM
squid               4 [d]       common [d]                                Squid - Optimising Web Delivery
subversion          1.10 [d]    common [d], server                        Apache Subversion
swig                3.0 [d]     common [d], complete                      Connects C/C++/Objective C to some high-level programming languages
varnish             6 [d]       common [d]                                Varnish HTTP cache
virt                rhel [d]    common [d]                                Virtualization module

Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled
""".strip()

DNF_MODULE_LIST_DOC = """
Updating Subscription Management repositories.
Name                Stream      Profiles                                  Summary
389-ds              1.4                                                   389 Directory Server (base)
ant                 1.10 [d]    common [d]                                Java build tool

Hint: [d]efault, [e]nabled, [x]disabled, [i]nstalled
""".strip()

DNF_MODULE_LIST_EXP1 = """
Updating Subscription Management repositories.
Cache-only enabled but no cache for 'rhel-8-for-x86_64-appstream-rpms', ignoring this repo.
Cache-only enabled but no cache for 'rhel-8-for-x86_64-baseos-rpms', ignoring this repo.
Cache-only enabled but no cache for 'rhel-8-for-x86_64-supplementary-rpms', ignoring this repo.
No matching Modules to list
""".strip()

DNF_MODULE_LIST_EXP2 = """
Updating Subscription Management repositories.
Name                Stream      Profiles                                  Summary
Error: xxx
""".strip()

DNF_MODULE_INFO = """
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

DNF_MODULE_INFO_EXP = """
Updating Subscription Management repositories.
Last metadata expiration check: 0:03:24 ago on Thu 25 Jul 2019 01:32:41 PM CST.
Unable to resolve argument abc
Error: No matching Modules to list
""".strip()


def test_dnf_module_list():
    module_list = DnfModuleList(context_wrap(DNF_MODULE_LIST))
    assert 'ant' in module_list
    assert module_list['httpd'].name == 'httpd'
    assert module_list['httpd'].stream == '2.4 [d][e]'


def test_dnf_module_list_exp():
    with pytest.raises(ValueError):
        DnfModuleList(context_wrap(DNF_MODULE_LIST_EXP1))

    with pytest.raises(SkipException):
        DnfModuleList(context_wrap(DNF_MODULE_LIST_EXP2))


def test_dnf_module_info():
    module_infos = DnfModuleInfo(context_wrap(DNF_MODULE_INFO))
    assert len(module_infos) == 3
    assert module_infos.modules == ['389-ds', 'ant', 'httpd']
    assert len(module_infos['httpd']) == 2
    assert module_infos['httpd'][0].name == 'httpd'
    assert module_infos['httpd'][0].version == '8000020190405071959'
    assert len(module_infos['httpd'][0].profiles) == 3
    assert module_infos['httpd'][0].default_profiles == 'common'
    assert module_infos['httpd'][1].summary == 'Apache HTTP Server'
    assert module_infos['httpd'][1].context == '9edba152'
    assert 'mod_http2-0:1.11.3-1.module+el8+2443+605475b7.x86_64' in module_infos['httpd'][1].artifacts


def test_dnf_module_info_exp():
    with pytest.raises(SkipException):
        DnfModuleInfo(context_wrap(DNF_MODULE_INFO_EXP))


def test_dnf_module_doc_examples():
    env = {
        'dnf_module_list': DnfModuleList(context_wrap(DNF_MODULE_LIST_DOC)),
        'dnf_module_info': DnfModuleInfo(context_wrap(DNF_MODULE_INFO))
    }
    failed, total = doctest.testmod(dnf_module, globs=env)
    assert failed == 0
