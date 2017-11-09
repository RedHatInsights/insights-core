from insights.parsers.tmpfilesd import TmpFilesD
from insights.combiners.tmpfilesd import AllTmpFiles
from insights.tests import context_wrap

SAP_CONF = """
# systemd tmpfiles exclude file for SAP
# SAP software stores some important files
# in /tmp which should not be deleted

# Exclude SAP socket and lock files
x /tmp/.sap*

# Exclude HANA lock file
x /tmp/.hdb*lock
""".strip()

DUPE_SAP_CONF = """
# systemd tmpfiles exclude file for SAP
# SAP software stores some important files
# in /tmp which should not be deleted

# Exclude SAP socket and lock files
r! /tmp/.sap*

# Exclude HANA lock file
x /tmp/.hdb*lock
""".strip()

DNF_CONF = """
# /usr/lib/tmpfiles.d/dnf.conf
r! /var/cache/dnf/*/*/download_lock.pid
r! /var/cache/dnf/*/*/metadata_lock.pid
r! /var/lib/dnf/rpmdb_lock.pid
e  /var/cache/dnf/ - - - 3
""".strip()

SAP_PATH = "/etc/tmpfiles.d/sap.conf"
DNF_PATH = "/etc/tmpfiles.d/dnf.conf"
DUPE_PATH = "/usr/lib/tmpfiles.d/sap.conf"


def test_all_tmpfiles_conf():
    data1 = TmpFilesD(context_wrap(SAP_CONF, SAP_PATH))
    data2 = TmpFilesD(context_wrap(DNF_CONF, DNF_PATH))
    all_data = AllTmpFiles([data1, data2])

    assert len(all_data.active_rules) == 2
    assert all_data.active_rules['/etc/tmpfiles.d/sap.conf'] == [{'type': 'x', 'path': '/tmp/.sap*', 'age': None,
                                                                  'gid': None, 'uid': None, 'argument': None, 'mode': None},
                                                                 {'type': 'x', 'path': '/tmp/.hdb*lock', 'age': None,
                                                                  'gid': None, 'uid': None, 'argument': None, 'mode': None}]
    assert all_data.active_rules['/etc/tmpfiles.d/dnf.conf'] == [{'type': 'r!', 'path': '/var/cache/dnf/*/*/download_lock.pid',
                                                                  'age': None, 'gid': None, 'uid': None, 'argument': None,
                                                                  'mode': None},
                                                                 {'type': 'r!', 'path': '/var/cache/dnf/*/*/metadata_lock.pid',
                                                                  'age': None, 'gid': None, 'uid': None, 'argument': None,
                                                                  'mode': None},
                                                                 {'type': 'r!', 'path': '/var/lib/dnf/rpmdb_lock.pid',
                                                                  'age': None, 'gid': None, 'uid': None, 'argument': None,
                                                                  'mode': None},
                                                                 {'type': 'e', 'path': '/var/cache/dnf/', 'age': '3',
                                                                  'gid': '-', 'uid': '-', 'argument': None, 'mode': '-'}]

    assert all_data.find_file('/tmp/.sap*') == {SAP_PATH: {'type': 'x', 'path': '/tmp/.sap*', 'age': None,
                                                           'mode': None, 'gid': None, 'uid': None,
                                                           'argument': None}}

    assert all_data.find_file('/tmp/.sap*')[SAP_PATH]['type'] == 'x'

    data3 = TmpFilesD(context_wrap(DUPE_SAP_CONF, DUPE_PATH))
    all_data = AllTmpFiles([data1, data3])
    # Ensure that only the last discovered of the rules are counted
    assert len(all_data.active_rules) == 2
    assert all_data.active_rules['/etc/tmpfiles.d/sap.conf'][0] == {'type': 'x', 'path': '/tmp/.sap*', 'age': None,
                                                                    'gid': None, 'uid': None, 'argument': None, 'mode': None}

    all_data = AllTmpFiles([data1, data2, data3])
    assert len(all_data.file_paths) == 3
    assert all_data.file_paths == ['/etc/tmpfiles.d/dnf.conf',
                                   '/etc/tmpfiles.d/sap.conf',
                                   '/usr/lib/tmpfiles.d/sap.conf']

    assert len(all_data.files) == 6
    assert all_data.files == set(['/var/cache/dnf/*/*/download_lock.pid',
                                  '/var/cache/dnf/*/*/metadata_lock.pid',
                                  '/var/lib/dnf/rpmdb_lock.pid',
                                  '/var/cache/dnf/',
                                  '/tmp/.sap*',
                                  '/tmp/.hdb*lock'])
