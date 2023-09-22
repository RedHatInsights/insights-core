import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import yumlog
from insights.parsers.yumlog import YumLog
from insights.tests import context_wrap

OKAY = """
May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
Jan 24 00:24:00 Updated: glibc-2.12-1.149.el6_6.4.x86_64
Jan 24 00:24:09 Updated: glibc-devel-2.12-1.149.el6_6.4.x86_64
Jan 24 00:24:10 Updated: nss-softokn-3.14.3-19.el6_6.x86_64
Jan 24 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
Jan 24 00:24:11 Updated: glibc-2.12-1.149.el6_6.4.i686
May 23 16:09:09 Erased: redhat-access-insights-batch
May 23 16:09:09 Erased: katello-agent
Jan 24 00:24:11 Updated: glibc-devel-2.12-1.149.el6_6.4.i686
""".strip()

OKAY2 = """
May 19 23:29:12 Installed: cyrus-sasl-md5-2.1.26-23.el7.x86_64
May 19 23:29:14 Installed: 389-ds-base-1.3.8.4-23.el7_6.x86_64
Jul 21 09:09:39 Updated: httpd-tools-2.4.6-93.el7.x86_64
Jul 21 09:09:39 Installed: mailcap-2.1.41-2.el7.noarch
Jul 26 23:24:36 Erased: systemd-219-46.el7.x86_64
Jul 28 23:24:36 Erased: systemd-219-67.el7.x86_64
Jul 21 09:09:40 Installed: httpd-2.4.6-93.el7.x86_64
Jul 20 09:09:40 Installed: httpd-2.4.6-97.el7.x86_64
""".strip()

ERROR = """
May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
Jan 24 00:24:00 Updated: glibc-2.12-1.149.el6_6.4.x86_64
Jan 24 00:24:09 Updated: glibc-devel-2.12-1.149.el6_6.4.x86_64
Bad
Jan 24 00:24:10 Updated: nss-softokn-3.14.3-19.el6_6.x86_64
Jan 24 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
Jan 24 00:24:11 Updated: glibc-2.12-1.149.el6_6.4.i686
May 23 16:09:09 Erased: redhat-access-insights-batch
Jan 24 00:24:11 Updated: glibc-devel-2.12-1.149.el6_6.4.i686
""".strip()

THROWS_PARSEEXCEPTION = """
Jan 24 00:24:09 Updated:
"""

DOC = """
May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
Jan 24 00:24:00 Updated: glibc-2.12-1.149.el6_6.4.x86_64
Jan 24 00:24:09 Updated: glibc-devel-2.12-1.149.el6_6.4.x86_64
Jan 24 00:24:10 Updated: nss-softokn-3.14.3-19.el6_6.x86_64
Jan 24 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
Jan 24 00:24:11 Updated: glibc-2.12-1.149.el6_6.4.i686
May 23 16:09:09 Erased: redhat-access-insights-batch
Jan 24 00:24:11 Updated: glibc-devel-2.12-1.149.el6_6.4.i686
""".strip()


def test_iteration():
    yl = YumLog(context_wrap(OKAY))
    indices = [i.idx for i in yl]
    assert indices == list(range(len(yl)))


def test_len():
    yl = YumLog(context_wrap(OKAY))
    assert len(yl) == 9


def test_present():
    yl = YumLog(context_wrap(OKAY))

    e = yl.present_packages.get('wget')
    assert e.pkg.name == 'wget'
    assert e.pkg.version == '1.14'

    e = yl.present_packages.get('openssl-libs')
    assert e.pkg.name == 'openssl-libs'
    assert e.pkg.version == '1.0.1e'


def test_packages_of():
    yl = YumLog(context_wrap(OKAY))

    pkgs = yl.packages_of('Installed')
    assert len(pkgs) == 1
    pkgs = yl.packages_of('Updated')
    assert len(pkgs) == 4
    pkgs = yl.packages_of(['Installed', 'Updated'])
    assert len(pkgs) == 5

    e = pkgs.get('openssl-libs')
    assert e.pkg.name == 'openssl-libs'
    assert e.pkg.version == '1.0.1e'

    pkgs = yl.packages_of(['Erased'])
    assert len(pkgs) == 2
    assert "katello-agent" in pkgs
    assert "redhat-access-insights-batch" in pkgs


def test_error():
    yl = YumLog(context_wrap(ERROR))

    e = yl.present_packages.get('wget')
    assert e.pkg.name == 'wget'
    assert e.pkg.version == '1.14'

    e = yl.present_packages.get('openssl-libs')
    assert e.pkg.name == 'openssl-libs'
    assert e.pkg.version == '1.0.1e'

    assert len(yl) == 8


def test_exception_throwing():
    with pytest.raises(ParseException) as e_info:
        YumLog(context_wrap(THROWS_PARSEEXCEPTION))
    assert "YumLog could not parse" in str(e_info.value)

    with pytest.raises(SkipComponent):
        YumLog(context_wrap(""))

    yl = YumLog(context_wrap(OKAY))
    with pytest.raises(KeyError) as ke:
        yl.packages_of(['Eras'])
    assert "Invalid State(s)" in str(ke)


def test_erased():
    yl = YumLog(context_wrap(OKAY))
    assert any(e.pkg.name == "redhat-access-insights-batch" for e in yl) is True
    assert any(e.pkg.name == "katello-agent" for e in yl) is True

    yl2 = YumLog(context_wrap(OKAY2))
    assert any(e.pkg.name == "systemd" for e in yl2) is True


def test_doc_example():
    env = {'yl': YumLog(context_wrap(DOC))}
    failed, total = doctest.testmod(yumlog, globs=env)
    assert failed == 0
