import pytest
import unittest
from falafel.tests import unordered_compare
from falafel.util.rpm import RpmPackage, get_package_nvr
from falafel.util.uname import Uname, UnameError, pad_release, parse_uname
from falafel.core.plugins import split_requirements, stringify_requirements, get_missing_requirements
from falafel.core import context


class TestUname(unittest.TestCase):

    def test_pad_release(self):
        self.assertEquals("390.0.0.el6", pad_release("390.el6"))
        self.assertEquals("390.12.0.el6", pad_release("390.12.el6"))
        self.assertEquals("390.12.0.0.el6", pad_release("390.12.el6", 5))
        self.assertRaises(ValueError, pad_release, '390.11.12.13.el6')

    def test_parse_uname(self):
        kernel_info = parse_uname("Linux hostname 3.16.2-200.fc20.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        self.assertEquals('3.16.2-200.fc20.x86_64', kernel_info['kernel'], "Full kernel version string doesn't match")
        self.assertEquals('Linux', kernel_info['name'], "Kernel name doesn't match")
        self.assertEquals('hostname', kernel_info['nodename'], "Nodename doesn't match")
        self.assertEquals('3.16.2', kernel_info['version'], "Version doesn't match")
        self.assertEquals(pad_release('200.fc20'), kernel_info['release'], "Release doesn't match")
        self.assertEquals('x86_64', kernel_info['arch'], "Architecture doesn't match")
        self.assertRaises(ValueError, parse_uname, "Linux hostname")

    def test_fixed_by(self):
        u = Uname.from_kernel("2.6.32-504.el6")
        self.assertEquals([], u.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6'))
        self.assertEquals(['2.6.32-600.el6'], u.fixed_by('2.6.32-600.el6'))
        self.assertEquals([], u.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6'))
        # Higher kernel version, lower release string should match
        self.assertEquals(['2.6.33-100.el6'], u.fixed_by('2.6.33-100.el6'))
        self.assertEquals(['2.6.32-600.el6'], u.fixed_by('2.6.32-220.1.el6', '2.6.32-600.el6'))

    def test_unknown_release(self):
        u = Uname.from_kernel("2.6.23-504.23.3.el6.revertBZ1169225")
        self.assertEquals(None, u._lv_release)
        fixed_by = u.fixed_by("2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5")
        self.assertEquals([], fixed_by)

    def test_fixed_by_rhel5(self):
        test_kernels = [
            (Uname("Linux oprddb1r5.circoncorp.com 2.6.18-348.el5 #1 SMP Wed Nov 28 21:22:00 EST 2012 x86_64 x86_64 x86_64 GNU/Linux"), []),
            (Uname("Linux srspidr1-3.expdemo.com 2.6.18-402.el5 #1 SMP Thu Jan 8 06:22:34 EST 2015 x86_64 x86_64 x86_64 GNU/Linux"), []),
            (Uname("Linux PVT-Dev1.pvtsolar.local 2.6.18-398.el5xen #1 SMP Tue Aug 12 06:30:31 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux"), []),
            (Uname.from_kernel("2.6.18-194.el5"),
                ["2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5"]),
            (Uname.from_kernel("2.6.18-128.el5"),
                ["2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5"]),

        ]
        for u, expected in test_kernels:
            print "Testing ", u.kernel
            fixed_by = u.fixed_by("2.6.18-128.39.1.el5", "2.6.18-238.40.1.el5", "2.6.18-308.13.1.el5", "2.6.18-348.el5")
            self.assertEquals(expected, fixed_by)

    def test_from_release(self):
        release = ("6", "4")
        from_release = Uname.from_release(release)
        from_nvr = Uname.from_kernel("2.6.32-358")
        assert str(from_release) == str(from_nvr)

        unknown_list = ["2.4.21-3", "2.6.9-4", "2.6.18-7", "2.6.32-70", "3.10.0-53"]
        known_list = [{'version': "2.4.21-4", 'rhel_release': ["3", "0"]},
                      {'version': "2.6.9-55", 'rhel_release': ["4", "5"]},
                      {'version': "2.6.18-308", 'rhel_release': ["5", "8"]},
                      {'version': "2.6.32-131.0.15", 'rhel_release': ["6", "1"]},
                      {'version': "3.10.0-123", 'rhel_release': ["7", "0"]}]
        for unknown_ver in unknown_list:
            unknown_uname = Uname("Linux hostname {version} #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux".format(version=unknown_ver))
            assert unknown_uname.rhel_release == ["-1", "-1"]
        for known_ver in known_list:
            known_uname = Uname("Linux hostname {version} #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux".format(version=known_ver['version']))
            assert known_uname.rhel_release == known_ver['rhel_release']

    def test_to_json(self):
        uname_obj = Uname("Linux hostname 3.10.0-229.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        uname_json_list = uname_obj.to_json()
        assert 'falafel.util.uname#Uname' == uname_json_list[0], "Module name does not match"
        uname_json = uname_json_list[1]
        assert '3.10.0-229.el7.x86_64' == uname_json['kernel'], "Full kernel version string doesn't match"
        assert 'Linux' == uname_json['name'], "Kernel name doesn't match"
        assert 'hostname' == uname_json['nodename'], "Nodename doesn't match"
        assert '3.10.0' == uname_json['version'], "Version doesn't match"
        assert '229.el7' == uname_json['release'], "Release doesn't match"
        assert ['7', '1'] == uname_json['rhel_release'], "RHEL Release doesn't match"
        assert 'x86_64' == uname_json['arch'], "Architecture doesn't match"
        assert 'GNU/Linux' == uname_json['os'], "OS doesn't match"
        assert 'x86_64' == uname_json['hw_platform'], "H/W platform doesn't match"
        assert 'x86_64' == uname_json['processor'], "Processor doesn't match"
        assert 'x86_64' == uname_json['machine'], "Machine doesn't match"
        assert 'Mon Sep 8 11:54:45 UTC 2014' == uname_json['kernel_date'], "Kernel date doesn't match"
        assert 'SMP' == uname_json['kernel_type'], "Kernel type doesn't match"

    def test_uname_eq(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left == right
        assert left == left_copy
        assert right == right_copy

        left_copy_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert not left == right_ver_rel
        assert left == left_copy_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left == right

        right = "3.16.2-200.el7.x86_64"
        assert left == right
        assert right == left

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        with pytest.raises(UnameError):
            left == right

        right_ver_rel = "3.16.2-200.10.1.1.el17.x86_65"
        with pytest.raises(UnameError):
            left == right

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.15.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left == right

        right_ver_rel = "3.155555.2-200.10.1.1.el17.x86_65"
        assert not left == right

        with pytest.raises(UnameError):
            right = Uname("Linuxhostname3.15.2-200.10.1.1.el7.x86_64#1SMPMonSep811:54:45UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")

        right_ver_rel = "31555552-200.10.1.1.el17.x86_65"
        with pytest.raises(UnameError):
            left == right_ver_rel

    def test_uname_ne(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left != right
        assert not left != left_copy
        assert not right != right_copy

        left_copy_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert left != right_ver_rel
        assert not left != left_copy_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left != right

        right = "3.16.2-200.el7.x86_64"
        assert not left != right
        assert not right != left

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.15.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left != right

        right_ver_rel = "3.155555.2-200.10.1.1.el17.x86_65"
        assert left != right

    def test_uname_lt(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left < right
        assert right < left
        assert not left < left_copy
        assert not right < right_copy

        left_copy_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert not left < right_ver_rel
        assert right_ver_rel < left
        assert not left < left_copy_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left < right
        assert not right < left

        right = "3.16.2-200.el7.x86_64"
        assert not left < right
        assert not right < left

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        with pytest.raises(UnameError):
            left < right

        right_ver_rel = "3.16.2-200.10.1.1.el17.x86_65"
        with pytest.raises(UnameError):
            left < right

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.15.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left < right

        right_ver_rel = "3.155555.2-200.10.1.1.el17.x86_65"
        assert not left < right

    def test_uname_le(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left <= right
        assert right <= left
        assert left <= left_copy
        assert right <= right_copy

        left_copy_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert not left <= right_ver_rel
        assert right_ver_rel <= left
        assert left <= left_copy_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left <= right
        assert right <= left

        right = "3.16.2-200.el7.x86_64"
        assert left <= right
        assert right <= left

    def test_uname_gt(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left > right
        assert not right > left
        assert not left > left_copy
        assert not right > right_copy

        left_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert left > right_ver_rel
        assert not right_ver_rel > left
        assert not left > left_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert not left > right
        assert not right > left

        right = "3.16.2-200.el7.x86_64"
        assert not left > right
        assert not right > left

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        with pytest.raises(UnameError):
            left > right

        right_ver_rel = "3.16.2-200.10.1.1.el17.x86_65"
        with pytest.raises(UnameError):
            left > right

        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.15.2-200.10.1.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left > right

        right_ver_rel = "3.155555.2-200.10.1.1.el17.x86_65"
        assert left > right

    def test_uname_ge(self):
        left = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        left_copy = Uname("Linux hostname 3.16.2-200.10.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right_copy = Uname("Linux hostname 3.16.2-200.9.1.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left >= right
        assert not right >= left
        assert left >= left_copy
        assert right >= right_copy

        left_ver_rel = "3.16.2-200.10.1.el7.x86_64"
        right_ver_rel = "3.16.2-200.9.1.el7.x86_64"
        assert left >= right_ver_rel
        assert not right_ver_rel >= left
        assert left >= left_ver_rel

        left = Uname("Linux hostname 3.16.2-200.0.0.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        right = Uname("Linux hostname 3.16.2-200.el7.x86_64 #1 SMP Mon Sep 8 11:54:45 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux")
        assert left >= right
        assert right >= left

        right = "3.16.2-200.el7.x86_64"
        assert left >= right
        assert right >= left

    def test_docker_uname(self):
        u = Uname("Linux 06a04d0354dc 4.0.3-boot2docker #1 SMP Wed May 13 20:54:49 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux")
        self.assertEquals("boot2docker", u.release)


class TestRpm(unittest.TestCase):

    def test_get_package_nvr(self):
        line = "zlib-1.2.3-29.el6.x86_64                                    Sun Mar 17 07:01:21 2013"
        self.assertEquals('zlib-1.2.3-29.el6', get_package_nvr(line))

        line = "xorg-x11-fonts-75dpi-7.2-9.1.el6.noarch                     Thu Oct 18 14:30:26 2012"
        self.assertEquals('xorg-x11-fonts-75dpi-7.2-9.1.el6', get_package_nvr(line))

    def test_rpm_package_construct_error(self):
        self.assertRaises(ValueError, RpmPackage, "9.9.4-15.P2.fc20.x86_64")
        self.assertRaises(ValueError, RpmPackage, "9.9.4-15.P2.AB20.x86_64")

    def test_rpm_package_construct(self):
        rpm_package = RpmPackage("bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64")
        self.assertEquals('bind-libs', rpm_package.name)
        self.assertEquals('9.8.2', rpm_package.version)
        self.assertEquals('0.17.rc1.el6_4.6', rpm_package.release)
        self.assertEquals('0.17.rc1', rpm_package.build)
        self.assertEquals('el6_4.6', rpm_package.dist)
        self.assertEquals('x86_64', rpm_package.arch)

        rpm_package = RpmPackage("bind-libs-9.8.2-0.17.rc1.el6_4.6")
        self.assertEquals('bind-libs', rpm_package.name)
        self.assertEquals('9.8.2', rpm_package.version)
        self.assertEquals('0.17.rc1.el6_4.6', rpm_package.release)
        self.assertEquals('0.17.rc1', rpm_package.build)
        self.assertEquals('el6_4.6', rpm_package.dist)
        self.assertEquals(None, rpm_package.arch)

        rpm_package = RpmPackage("a-package-name-9.9.4-15.P2.fc20.x86_64")
        self.assertEquals('a-package-name', rpm_package.name)
        self.assertEquals('9.9.4', rpm_package.version)
        self.assertEquals('15.P2.fc20', rpm_package.release)
        self.assertEquals('15.P2', rpm_package.build)
        self.assertEquals('fc20', rpm_package.dist)
        self.assertEquals('x86_64', rpm_package.arch)

    def test_name_dist_match(self):
        left = RpmPackage("bind-libs-9.8.2.1-0.17.rc2.el6_4.6.x86_64")
        right = RpmPackage("bind-libs-9.8.2-0.17.rc2.el6_4.6.x86_64")
        self.assertTrue(left.name_dist_match(right))
        self.assertTrue(right.name_dist_match(left))
        self.assertTrue(left.name_dist_match("bind-libs-9.8.2-0.17.rc2.el6_4.6.x86_64"))

        right = RpmPackage("binding-libs-9.8.2-0.17.rc2.el6_4.6.x86_64")
        self.assertFalse(left.name_dist_match(right))
        self.assertFalse(right.name_dist_match(left))

        right = RpmPackage("bind-libs-9.8.2-0.17.rc2.el5.6.x86_64")
        self.assertFalse(left.name_dist_match(right))
        self.assertFalse(right.name_dist_match(left))

        right = RpmPackage("binding-libs-9.8.2-0.17.rc2.el5.6.x86_64")
        self.assertFalse(left.name_dist_match(right))
        self.assertFalse(right.name_dist_match(left))

    def test_nonstandard_package(self):
        pkg = RpmPackage("firefox-1.5.0.12-3.el5-i386")
        self.assertEquals("i386", pkg.arch)
        self.assertEquals("firefox", pkg.name)
        self.assertEquals("1.5.0.12", pkg.version)
        self.assertEquals("3.el5", pkg.release)


class t(object):

    def __init__(self, n):
        self.serializable_id = self.n = n

    def __eq__(self, item):
        return hasattr(item, "n") and item.n == self.n

    def __lt__(self, item):
        return self.n < item.n

    def __hash__(self):
        return self.n.__hash__()

    def __repr__(self):
        return self.n


def dummy_dict(l):
    return {k: 1 for k in l}


class TestReducerRequirements(unittest.TestCase):

    requires = [t("a"), t("b"), [t("d"), t("e")], t("c"), [t("f"), t("g")]]

    def test_split(self):
        expected = ([t("a"), t("b"), t("c")], [[t("d"), t("e")], [t("f"), t("g")]])
        result = split_requirements(self.requires)
        assert expected == result

    def test_stringify(self):
        expected = "All: ['a', 'b', 'c'] Any: ['d', 'e'] Any: ['f', 'g']"
        result = stringify_requirements(self.requires)
        assert expected == result

    def test_missing(self):
        missing_none = dummy_dict([t("a"), t("b"), t("c"), t("d"), t("e"), t("f"), t("g")])
        assert get_missing_requirements(self.requires, missing_none) is None
        missing_partial_any = dummy_dict([t("a"), t("b"), t("c"), t("d"), t("g")])
        assert get_missing_requirements(self.requires, missing_partial_any) is None
        missing_any = dummy_dict([t("a"), t("b"), t("c"), t("f"), t("g")])
        result = get_missing_requirements(self.requires, missing_any)
        assert result == ([], [[t("d"), t("e")]])
        missing_all = dummy_dict([t("a"), t("c"), t("d"), t("e"), t("f"), t("g")])
        result = get_missing_requirements(self.requires, missing_all)
        assert result == ([t("b")], [])


class TestContext(unittest.TestCase):

    def setUp(self):
        self.ctx = context.Context()

    def test_sane_defaults(self):
        self.assertEquals(None, self.ctx.hostname)
        self.assertEquals(["-1", "-1"], self.ctx.version)

    def test_product_available(self):
        self.ctx.osp.role = "Controller"
        self.assertTrue(self.ctx.osp)
        self.assertEquals("Controller", self.ctx.osp.role)

    def test_product_not_available(self):
        self.assertFalse(bool(self.ctx.osp))
        self.assertEquals(None, self.ctx.osp.role)

    def test_non_product_member(self):
        self.assertRaises(AttributeError, lambda: self.ctx.invalid_product)


class TestCompare(unittest.TestCase):

    def test_str(self):
        unordered_compare("foo", "foo")
        unordered_compare(u"foo", "foo")
        with pytest.raises(AssertionError):
            unordered_compare("foo", "bar")

    def test_num(self):
        unordered_compare(1, 1)
        unordered_compare(1.1, 1.1)
        with pytest.raises(AssertionError):
            unordered_compare(1, 2)

    def test_list(self):
        unordered_compare([1, 2, 3], [1, 2, 3])
        unordered_compare([2, 3, 4], [4, 3, 2])
        with pytest.raises(AssertionError):
            unordered_compare([1, 2, 3], [2, 3, 4])

    def test_dict(self):
        unordered_compare({"foo": 1}, {"foo": 1})
        unordered_compare({"foo": 1, "bar": 2}, {"bar": 2, "foo": 1})
        with pytest.raises(AssertionError):
            unordered_compare({"foo": 1}, {"foo": 2})

        with pytest.raises(AssertionError):
            unordered_compare({"foo": 1, "bar": [1, 2, 3]}, {"foo": 1, "bar": [0, 1, 2]})

    def test_deep_nest(self):
        a = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}
        b = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}

        unordered_compare(a, b)

        with pytest.raises(AssertionError):
            b["stuff"]["abba"][0]["foo"] = "cake"
            unordered_compare(a, b)
