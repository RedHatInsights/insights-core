import doctest
from insights.parsers import dnf_module
from insights.parsers.dnf_module import DnfModuleList
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


def test_dnf_module_list():
    module_list = DnfModuleList(context_wrap(DNF_MODULE_LIST))
    assert 'ant' in module_list
    assert module_list['httpd'].name == 'httpd'
    assert module_list['httpd'].stream == '2.4 [d][e]'


# def test_dnf_module_doc_examples():
#     failed, total = doctest.testmod(
#         dnf_modules,
#         globs={'dnf_modules': dnf_modules.DnfModules(context_wrap(DNF_MODULES_INPUT))}
#     )
#     assert failed == 0
