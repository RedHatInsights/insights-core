import pytest
from insights.parsers import uname
from insights.tests import context_wrap

from distutils.version import LooseVersion, StrictVersion

import doctest


UNAME1 = "Linux foo.example.com 2.6.32-504.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux"
UNAME2 = "Linux rhel7box 3.10.0-229.el7.x86_64 #1 SMP Mon Mar 3 13:32:45 EST 2014 x86_64 x86_64 x86_64 GNU/Linux"
UNAME3 = "Linux map1a 2.6.18-53.el5PAE #1 SMP Wed Oct 10 16:48:18 EDT 2007 i686 i686 i386 GNU/Linux"
UNAME4 = "Linux cvlvtsmsrv01 3.10.0-229.el7.x86_64 #1 SMP Thu Jan 29 18:37:38 EST 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME5 = "Linux cvlvtsmsrv01 2.6.32-504.8.2.bgq.el6.x86_64 #1 SMP Thu Jan 29 18:37:38 EST 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_1 = "Linux localhost.localdomain 2.6.24.7-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_1pre = "Linux localhost.localdomain 2.6.24.6-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_1pre2 = "Linux localhost.localdomain 2.6.24-101.el5.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_1post = "Linux localhost.localdomain 2.6.24.7-101.1.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_1post2 = "Linux localhost.localdomain 2.6.25-101.el5.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_2 = "Linux localhost.localdomain 2.6.33.9-rt31.66.el6rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_2pre = "Linux localhost.localdomain 2.6.33.9-rt31.65.el6rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_2pre2 = "Linux localhost.localdomain 2.6.33-65.el6.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_2post = "Linux localhost.localdomain 2.6.34.1-rt31.65.el6rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_2post2 = "Linux localhost.localdomain 2.6.34-65.el6.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_3 = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_3pre = "Linux localhost.localdomain 3.10.0-326.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_3pre2 = "Linux localhost.localdomain 3.9.1-327.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_3post = "Linux localhost.localdomain 3.10.0-328.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_RT_3post2 = "Linux localhost.localdomain 3.10.1-327.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

UNAME_CVE_2016_0728_1 = 'Linux hostname.example.com 3.10.0-229.1.2.rt56.141.2.el7_1.x86_64 #1 SMP Fri Dec 19 12:09:25 EST 2014 x86_64 x86_64 x86_64 GNU/Linux'

UNAME_BLANK_LINE = """
Linux qqhrycsq2 2.6.32-279.el6.x86_64 #1 SMP Wed Jun 13 18:24:36 EDT 2012 x86_64 x86_64 x86_64 GNU/Linux

""".strip()

UNAME_FOREMAN_DEBUG = """
COMMAND> uname -a
Linux qqhrycsq2 2.6.32-279.el6.x86_64 #1 SMP Wed Jun 13 18:24:36 EDT 2012 x86_64 x86_64 x86_64 GNU/Linux
""".strip()

UNAME_ERROR_BLANK = ""
UNAME_ERROR_TOO_SHORT = "Linux localhost.localdomain"
UNAME_ERROR_TOO_SHORT2 = "Linux 2.6.32-279.el6.x86_64"
UNAME_ERROR_TOO_SHORT3 = "2.6.32-279.el6.x86_64"
UNAME_ERROR_ABBR_BAD_NVR = 'Linux bad-nvr 2'
UNAME_ERROR_TOO_MANY_REL_PARTS = 'Linux bad-parts 3.10.1.4.16-327.204.108.59.11.el7.x86_64'


def test_uname():
    uname1 = uname.Uname(context_wrap(UNAME1))
    uname2 = uname.Uname(context_wrap(UNAME2))
    uname3 = uname.Uname(context_wrap(UNAME3))
    uname4 = uname.Uname(context_wrap(UNAME4))
    uname5 = uname.Uname(context_wrap(UNAME5))
    uname6 = uname.Uname(context_wrap(UNAME_BLANK_LINE))
    uname7 = uname.Uname(context_wrap(UNAME_FOREMAN_DEBUG))

    # Test all the properties
    assert uname1.arch == 'x86_64'
    assert uname1.hw_platform == 'x86_64'
    assert uname1.kernel == '2.6.32-504.el6.x86_64'
    assert uname1.kernel_date == 'Tue Sep 16 01:56:35 EDT 2014'
    assert uname1.kernel_type == 'SMP'
    assert uname1.machine == 'x86_64'
    assert uname1.name == 'Linux'
    assert uname1.nodename == 'foo.example.com'
    assert uname1.os == 'GNU/Linux'
    assert uname1.processor == 'x86_64'
    assert uname1.redhat_release == uname.RedhatRelease(major=6, minor=6)
    assert uname1.release == '504.el6'
    assert uname1.release_arch == '504.el6.x86_64'
    assert uname1.release_tuple == (6, 6,)
    assert uname1.rhel_release == ['6', '6']
    assert uname1.ver_rel == '2.6.32-504.el6'
    assert uname1.version == '2.6.32'
    assert uname1._lv_release == LooseVersion('504.0.0.0.el6')
    assert uname1._lv_version == LooseVersion('2.6.32')
    assert uname1._rel_maj == '504'
    assert uname1._sv_version == StrictVersion('2.6.32')

    # Test the equality and inequality operators
    assert uname1 != uname2
    assert uname2 == uname4
    assert uname2 > uname1
    assert uname4 >= uname3
    assert uname3 < uname2
    assert uname1 <= uname4

    # String and repr tests
    assert str(uname1) == 'version: 2.6.32; release: 504.el6; rel_maj: 504; lv_release: 504.0.0.0.el6'
    assert repr(uname1) == "<Uname 'version: 2.6.32; release: 504.el6; rel_maj: 504; lv_release: 504.0.0.0.el6'>"

    # Just a release
    uname_from_release = uname.Uname.from_release('7.2')
    assert uname_from_release.version == '3.10.0'
    assert uname_from_release.release == '327'

    # test obscure bits of parse_nvr()
    # Strict version value error
    nvr = uname.Uname.parse_nvr('quodge-327.204.el7.x86_64')
    assert nvr['version'] == 'quodge'
    assert nvr['_sv_version'] is None
    assert nvr['_lv_version'] == 'quodge'
    assert nvr['_lv_release'] == '327.204.0.0.el7'

    kernel1 = uname1  # 2.6.32-504.el6.x86_64
    assert [] == kernel1.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6')
    assert ['2.6.32-600.el6'] == kernel1.fixed_by('2.6.32-600.el6')
    assert [] == kernel1.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6')
    assert ['2.6.33-100.el6'] == kernel1.fixed_by('2.6.33-100.el6')
    assert ['2.6.32-600.el6'] == kernel1.fixed_by('2.6.32-220.1.el6', '2.6.32-600.el6')
    assert ['2.6.32-504.1.el6'] == kernel1.fixed_by('2.6.32-504.1.el6')

    # test that 5 sections in a RH-released kernel name are not a problem
    kernel5 = uname5  # 2.6.32-504.8.2.bgq.el6.x86_64
    assert '2.6.32-504.8.2.bgq.el6' == kernel5.ver_rel

    assert uname6._sv_version == StrictVersion('2.6.32')
    assert uname6.arch == 'x86_64'
    assert uname6.hw_platform == 'x86_64'
    assert uname6.kernel == '2.6.32-279.el6.x86_64'
    assert uname6.kernel_date == 'Wed Jun 13 18:24:36 EDT 2012'

    assert uname7._sv_version == StrictVersion('2.6.32')
    assert uname7.arch == 'x86_64'
    assert uname7.hw_platform == 'x86_64'
    assert uname7.kernel == '2.6.32-279.el6.x86_64'
    assert uname7.kernel_date == 'Wed Jun 13 18:24:36 EDT 2012'

    # RT kernel tests
    uname_rt_1 = uname.Uname(context_wrap(UNAME_RT_1))
    assert uname_rt_1
    assert uname_rt_1.version == "2.6.24.7"
    assert uname_rt_1._sv_version is None
    assert uname_rt_1._lv_version == "2.6.24.7"
    assert uname_rt_1.release == "101.el5rt"
    assert uname_rt_1.arch == "x86_64"
    assert uname_rt_1 == UNAME_RT_1
    assert uname_rt_1 == uname.Uname.from_uname_str(UNAME_RT_1)
    assert uname_rt_1 > UNAME_RT_1pre
    assert uname_rt_1 > UNAME_RT_1pre2
    assert uname_rt_1 < UNAME_RT_1post
    assert uname_rt_1 < UNAME_RT_1post2
    assert uname_rt_1.rhel_release == ['-1', '-1']

    uname_rt_2 = uname.Uname(context_wrap(UNAME_RT_2))
    assert uname_rt_2
    assert uname_rt_2.version == "2.6.33.9"
    assert uname_rt_2._sv_version is None
    assert uname_rt_2._lv_version == "2.6.33.9"
    assert uname_rt_2.release == "rt31.66.el6rt"
    assert uname_rt_2.arch == "x86_64"
    assert uname_rt_2 == UNAME_RT_2
    assert uname_rt_2 == uname.Uname.from_uname_str(UNAME_RT_2)
    assert uname_rt_2 > UNAME_RT_2pre
    assert uname_rt_2 > UNAME_RT_2pre2
    assert uname_rt_2 < UNAME_RT_2post
    assert uname_rt_2 < UNAME_RT_2post2
    assert uname_rt_2.rhel_release == ['-1', '-1']

    uname_rt_3 = uname.Uname(context_wrap(UNAME_RT_3))
    assert uname_rt_3
    assert uname_rt_3.version == "3.10.0"
    assert uname_rt_3._sv_version == "3.10.0"
    assert uname_rt_3._lv_version == "3.10.0"
    assert uname_rt_3.release == "327.rt56.204.el7"
    assert uname_rt_3.arch == "x86_64"
    assert uname_rt_3 == UNAME_RT_3
    assert uname_rt_3 == uname.Uname.from_uname_str(UNAME_RT_3)
    assert uname_rt_3 > UNAME_RT_3pre
    assert uname_rt_3 > UNAME_RT_3pre2
    assert uname_rt_3 < UNAME_RT_3post
    assert uname_rt_3 < UNAME_RT_3post2
    assert uname_rt_3.rhel_release == ['7', '2']


def test_uname_errors():
    with pytest.raises(uname.UnameError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_BLANK))
    assert 'Empty uname line' in str(e_info.value)
    with pytest.raises(uname.UnameError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_TOO_SHORT))
    assert "Uname string appears invalid" in str(e_info.value)
    with pytest.raises(uname.UnameError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_TOO_SHORT2))
    assert "Uname string appears invalid" in str(e_info.value)
    with pytest.raises(uname.UnameError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_TOO_SHORT3))
    assert "Uname string appears invalid" in str(e_info.value)
    with pytest.raises(uname.UnameError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_ABBR_BAD_NVR))
    assert "Too few parts in the uname version-release" in str(e_info.value)
    with pytest.raises(ValueError) as e_info:
        uname.Uname(context_wrap(UNAME_ERROR_TOO_MANY_REL_PARTS))
    assert "Too many sections encountered" in str(e_info.value)


def test_uname_from_rules():
    cve_2016_0728 = uname.Uname(context_wrap(UNAME_CVE_2016_0728_1))
    assert cve_2016_0728.kernel == '3.10.0-229.1.2.rt56.141.2.el7_1.x86_64'


def test_pad_release():
    assert "390.0.0.el6" == uname.pad_release("390.el6")
    assert "390.12.0.el6" == uname.pad_release("390.12.el6")
    assert "390.12.0.0.el6" == uname.pad_release("390.12.el6", 5)
    with pytest.raises(ValueError):
        uname.pad_release('390.11.12.13.el6')


def test_fixed_by():
    u = uname.Uname.from_uname_str("Linux qqhrycsq2 2.6.32-504.el6.x86_64 #1 SMP Wed Jun 13 18:24:36 EDT 2012 x86_64 x86_64 x86_64 GNU/Linux")
    assert [] == u.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6')
    assert ['2.6.32-600.el6'] == u.fixed_by('2.6.32-600.el6')
    assert [] == u.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6')
    # Higher kernel version, lower release string should match
    assert ['2.6.33-100.el6'] == u.fixed_by('2.6.33-100.el6')
    assert ['2.6.32-600.el6'] == u.fixed_by('2.6.32-220.1.el6', '2.6.32-600.el6')


def test_unknown_release():
    u = uname.Uname.from_kernel("2.6.23-504.23.3.el6.revertBZ1169225")
    assert "504.23.3.0.el6" == u._lv_release
    fixed_by = u.fixed_by("2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5")
    assert [] == fixed_by


def test_fixed_by_rhel5():
    test_kernels = [
        (uname.Uname.from_uname_str("Linux oprddb1r5.example.com 2.6.18-348.el5 #1 SMP Wed Nov 28 21:22:00 EST 2012 x86_64 x86_64 x86_64 GNU/Linux"), []),
        (uname.Uname.from_uname_str("Linux srspidr1-3.example2.com 2.6.18-402.el5 #1 SMP Thu Jan 8 06:22:34 EST 2015 x86_64 x86_64 x86_64 GNU/Linux"), []),
        (uname.Uname.from_uname_str("Linux PVT-Dev1.pvtsolar.local 2.6.18-398.el5xen #1 SMP Tue Aug 12 06:30:31 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux"), []),
        (uname.Uname.from_kernel("2.6.18-194.el5"),
            ["2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5"]),
        (uname.Uname.from_kernel("2.6.18-128.el5"),
            ["2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5"]),

    ]
    for u, expected in test_kernels:
        fixed_by = u.fixed_by("2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5")
        assert expected == fixed_by


def test_from_release():
    release = ("6", "4")
    from_release = uname.Uname.from_release(release)
    from_nvr = uname.Uname.from_kernel("2.6.32-358")
    assert str(from_release) == str(from_nvr)

    unknown_list = ["2.4.21-3", "2.6.9-4", "2.6.18-7", "2.6.32-70", "3.10.0-53"]
    known_list = [{'version': "2.4.21-4", 'rhel_release': ["3", "0"]},
                  {'version': "2.6.9-55", 'rhel_release': ["4", "5"]},
                  {'version': "2.6.18-308", 'rhel_release': ["5", "8"]},
                  {'version': "2.6.32-131.0.15", 'rhel_release': ["6", "1"]},
                  {'version': "3.10.0-123", 'rhel_release': ["7", "0"]}]
    for unknown_ver in unknown_list:
        unknown_uname = uname.Uname.from_uname_str("Linux hostname {version} #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux".format(version=unknown_ver))
        assert unknown_uname.rhel_release == ["-1", "-1"]
    for known_ver in known_list:
        known_uname = uname.Uname.from_uname_str("Linux hostname {version} #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux".format(version=known_ver['version']))
        assert known_uname.rhel_release == known_ver['rhel_release']


def test_uname_version_comparisons():
    # ### Test comparisons between Uname objects at the version level ###
    left__str = "Linux hostname 3.10.0-123.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    right_str = "Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    left = uname.Uname.from_uname_str(left__str)
    left_copy = uname.Uname.from_uname_str(left__str)
    right = uname.Uname.from_uname_str(right_str)
    right_copy = uname.Uname.from_uname_str(right_str)

    # Equality tests
    assert not left == right
    assert left == left_copy
    assert right == right_copy
    # Inequality tests
    assert left != right
    assert not left != left_copy
    assert not right != right_copy
    # Less than tests
    assert left < right
    assert not right < left
    assert not left < left_copy
    assert not right < right_copy
    # Less than or equal to tests
    assert left <= right
    assert not right <= left
    assert left <= left_copy
    assert right <= right_copy
    # Greater than tests
    assert not left > right
    assert right > left
    assert not left > left_copy
    assert not right > right_copy
    # Greater than or equal to tests
    assert not left >= right
    assert right >= left
    assert left >= left_copy
    assert right >= right_copy


def test_uname_release_comparisons():
    # ### Test comparisons between Uname objects at the release level ###
    left__str = "Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    right_str = "Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    left = uname.Uname.from_uname_str(left__str)
    left_copy = uname.Uname.from_uname_str(left__str)
    right = uname.Uname.from_uname_str(right_str)
    right_copy = uname.Uname.from_uname_str(right_str)

    # Equality tests
    assert not left == right
    assert left == left_copy
    assert right == right_copy
    # Inequality tests
    assert left != right
    assert not left != left_copy
    assert not right != right_copy
    # Less than tests
    assert not left < right
    assert right < left
    assert not left < left_copy
    assert not right < right_copy
    # Less than or equal to tests
    assert not left <= right
    assert right <= left
    assert left <= left_copy
    assert right <= right_copy
    # Greater than tests
    assert left > right
    assert not right > left
    assert not left > left_copy
    assert not right > right_copy
    # Greater than or equal to tests
    assert left >= right
    assert not right >= left
    assert left >= left_copy
    assert right >= right_copy


def test_uname_vrastring_comparisons():
    # ### Test comparisons between Uname objects and ver-rel-arch strings ###
    left__str = "Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    left = uname.Uname.from_uname_str(left__str)
    left_ver_rel = "3.16.2-200.10.1.el7.x86_64"
    right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
    # Equality tests
    assert not left == right_ver_rel
    assert left == left_ver_rel
    # Inequality tests
    assert left != right_ver_rel
    assert not left != left_ver_rel
    # Less than tests
    assert not left < right_ver_rel
    assert right_ver_rel < left
    assert not left < left_ver_rel
    # Less than or equal to tests
    assert not left <= right_ver_rel
    assert right_ver_rel <= left
    assert left <= left_ver_rel
    # Greater than tests
    assert left > right_ver_rel
    assert not right_ver_rel > left
    assert not left > left_ver_rel
    # Greater than or equal to tests
    assert left >= right_ver_rel
    assert not right_ver_rel >= left
    assert left >= left_ver_rel


def test_uname_release_length_comparisons():
    # ### Test comparisons between Uname objects where releases loosely match ###
    minor_left__str = "Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    minor_right_str = "Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"
    left = uname.Uname.from_uname_str(minor_left__str)
    right = uname.Uname.from_uname_str(minor_right_str)
    # Equality tests
    assert left == right
    # Inequality tests
    assert not left != right
    # Less than tests
    assert not left < right
    assert not right < left
    # Less than or equal to tests
    assert left <= right
    assert right <= left
    # Greater than tests
    assert not left > right
    assert not right > left
    # Greater than or equal to tests
    assert left >= right
    assert right >= left


def test_docker_uname():
    u = uname.Uname.from_uname_str("Linux 06a04d0354dc 4.0.3-boot2docker #1 SMP Wed May 13 20:54:49 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux")
    assert "boot2docker" == u.release


uname_line = 'Linux server1.example.com 2.6.32-504.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux'


# Because tests are done at the module level, we have to put all the shared
# parser information in the one environment.  Fortunately this is normal.
def test_uname_doc_examples():
    env = {
        'Uname': uname.Uname,
        'uname': uname.Uname(context_wrap(uname_line)),
    }
    failed, total = doctest.testmod(uname, globs=env)
    assert failed == 0
