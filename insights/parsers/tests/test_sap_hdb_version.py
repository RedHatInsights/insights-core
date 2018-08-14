from insights.parsers import SkipException, sap_hdb_version
from insights.parsers.sap_hdb_version import HDBVersion
from insights.tests import context_wrap
import pytest
import doctest

HDB_VER_1 = """
HDB version info:
  version:             2.00.030.00.1522210459
  branch:              hanaws
  machine config:      linuxx86_64
  git hash:            bb2ff6b25b8eab5ab382c170a43dc95ae6ce298f
  git merge time:      2018-03-28 06:14:19
  weekstone:           2018.13.0
  cloud edition:       0000.00.00
  compile date:        2018-03-28 06:19:13
  compile host:        ld2221
  compile type:        rel
""".strip()

HDB_VER_2 = """
HDB version info:
  version:             2.00.020.00.1500920972
  branch:              fa/hana2sp02
  git hash:            7f63b0aa11dca2ea54d450aa302319302c2eeaca
  git merge time:      2017-07-24 20:29:32
  weekstone:           0000.00.0
  compile date:        2017-07-24 20:35:12
  compile host:        ld4551
  compile type:        rel
""".strip()

HDB_VER_NG_1 = """
su: user hxeadm does not exist
""".strip()

HDB_VER_NG_2 = """
HDB version info:
  version:             2.00.020.1500920972
  branch:              fa/hana2sp02
  git hash:            7f63b0aa11dca2ea54d450aa302319302c2eeaca
  git merge time:      2017-07-24 20:29:32
  weekstone:           0000.00.0
  compile date:        2017-07-24 20:35:12
  compile host:        ld4551
""".strip()


def test_HDBVersion_doc():
    env = {
            'hdb_ver': HDBVersion(context_wrap(HDB_VER_1)),
          }
    failed, total = doctest.testmod(sap_hdb_version, globs=env)
    assert failed == 0


def test_HDBVersion_ng():
    with pytest.raises(SkipException) as e_info:
        HDBVersion(context_wrap(HDB_VER_NG_1))
    assert "Incorrect content." in str(e_info.value)

    with pytest.raises(SkipException) as e_info:
        HDBVersion(context_wrap(HDB_VER_NG_2))
    assert "Incorrect HDB version: 2.00.020.1500920972" in str(e_info.value)


def test_HDBVersion_1():
    hdb_ver = HDBVersion(context_wrap(HDB_VER_1))
    assert hdb_ver['branch'] == 'hanaws'
    assert hdb_ver['compile type'] == 'rel'
    assert hdb_ver['weekstone'] == '2018.13.0'


def test_HDBVersion_2():
    hdb_ver = HDBVersion(context_wrap(HDB_VER_2))
    assert hdb_ver['branch'] == 'fa/hana2sp02'
    assert hdb_ver['compile host'] == 'ld4551'
    assert 'compile_type' not in hdb_ver
    assert hdb_ver['weekstone'] == '0000.00.0'
    assert hdb_ver.major == '2'
    assert hdb_ver.revision == '020'
