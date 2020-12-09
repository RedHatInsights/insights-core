from insights.parsers import ls_ipa_idoverride_memberof
from insights.parsers.ls_ipa_idoverride_memberof import LsIPAIdoverrideMemberof
from insights.tests import context_wrap
import doctest

LS_IPA_IDOVERRIDEMEMBEROF = """
/usr/share/ipa/ui/js/plugins/idoverride-memberof:
total 0
drwxr-xr-x. 2 0 0 0 Nov 11 11:44 .
drwxr-xr-x. 4 0 0 0 Nov 11 11:44 ..
-rw-rw-r--. 1 0 0 0 Nov 11 11:44 idoverride-memberof.js
-rw-rw-r--. 1 0 0 0 Nov 11 11:44 idoverride-admemberof.js
"""


def test_ls_ipa_idoverride_memberof():
    ls_ipa_idoverride_memberof = LsIPAIdoverrideMemberof(context_wrap(LS_IPA_IDOVERRIDEMEMBEROF))
    assert '/usr/share/ipa/ui/js/plugins/idoverride-memberof' in ls_ipa_idoverride_memberof
    assert ls_ipa_idoverride_memberof.files_of('/usr/share/ipa/ui/js/plugins/idoverride-memberof') == ['idoverride-memberof.js', 'idoverride-admemberof.js']


def test_ls_ipa_idoverride_memberof_doc():
    failed_count, tests = doctest.testmod(
        ls_ipa_idoverride_memberof,
        globs={'ls_ipa_idoverride_memberof': ls_ipa_idoverride_memberof.LsIPAIdoverrideMemberof(context_wrap(LS_IPA_IDOVERRIDEMEMBEROF))}
    )
    assert failed_count == 0
