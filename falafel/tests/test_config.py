import unittest
import pytest
import shlex

from falafel.config import InsightsDataSpecConfig, SimpleFileSpec, PatternSpec, CommandSpec, format_rpm, All, First, group_wrap
from falafel.config import DockerHostCommandSpec, SpecPathError
from falafel.util.command import retarget_command_for_mountpoint, sh_join
from falafel.config import HostTarget, DockerImageTarget, DockerContainerTarget


class TestSimpleFileSpec(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dummy_path = r'path/to/thing'
        cls.with_dollar = cls.dummy_path + r'$'

    def setUp(self):
        self.spec = SimpleFileSpec(self.dummy_path)

    def tearDown(self):
        self.spec = None

    def test_get_path(self):
        self.assertEqual(self.dummy_path, self.spec.get_path())

    def test_get_regex(self):
        self.assertEqual(self.with_dollar, self.spec.get_regex().pattern)

    def test_get_regex_prefix(self):
        prefix = 'prefix'
        self.assertEqual(prefix + self.with_dollar, self.spec.get_regex(prefix=prefix).pattern)

    def test_get_regex_suffix(self):
        suffix = 'suffix'
        self.assertEqual(self.dummy_path + suffix, self.spec.get_regex(suffix=suffix).pattern)

    def test_get_preferred_path(self):
        self.assertRaises(NotImplementedError, self.spec.get_preferred_path)

    def test_default_is_multi_output(self):
        self.assertFalse(self.spec.is_multi_output())

    def test_default_is_large(self):
        self.assertFalse(self.spec.is_large())

    def test_get_dynamic_args(self):
        self.assertEqual(self.spec.get_dynamic_args(), [])


class TestAbsolutePathFileSpec(unittest.TestCase):

    def test_absolute_path_raises_specpatherror(self):
        with self.assertRaises(SpecPathError):
            self.spec = SimpleFileSpec('/etc/php.ini')


class TestPatternSpec(TestSimpleFileSpec):

    def setUp(self):
        self.spec = PatternSpec(self.dummy_path)

    def test_default_is_multi_output(self):
        self.assertTrue(self.spec.is_multi_output())

    def test_default_is_large(self):
        self.assertFalse(self.spec.is_large())

    def test_matches(self):
        self.assertTrue(self.spec.matches('/path/to/thing'))
        self.assertFalse(self.spec.matches('/some/other/path'))


class TestCommandSpec(unittest.TestCase):

    def setUp(self):
        self.command_string = "/sbin/ethtool -a {iface}"
        self.spec = CommandSpec(self.command_string, iface=r"\S+")

    def test_string_representation(self):
        self.assertTrue(self.spec.__str__() is not None)

    def test_default_is_multi_output(self):
        self.assertTrue(self.spec.is_multi_output())

    def test_default_is_large(self):
        self.assertFalse(self.spec.is_large())

    def test_mangle_name(self):
        command = "/sbin/ethtool -a"
        expected = 'ethtool_-a'
        actual = CommandSpec.mangle_command(command)
        self.assertEqual(expected, actual)

    def test_get_path_multi_output(self):
        actual = self.spec.get_path()
        expected = 'ethtool_-a_(?P<iface>\\S+)'
        self.assertEqual(expected, actual)

    def test_get_path_context_dict(self):
        match = self.spec.get_regex().match("stuff/ethtool_-a_eth0")
        actual = match.groupdict()
        expected = {"iface": "eth0"}
        self.assertEqual(expected, actual)

    def test_get_path_non_multi_output(self):
        command_string = "/sbin/ethtool -a"
        spec = CommandSpec(command_string)
        actual = spec.get_path()
        expected = 'ethtool_-a'
        self.assertEqual(expected, actual)

    def test_get_for_uploader_non_multi_output(self):
        command_string = "/sbin/ethtool -a"
        spec = CommandSpec(command_string)
        actual = spec.get_for_uploader()
        self.assertEqual(command_string, actual)

    def test_get_for_uploader_multi_output(self):
        expected = "/sbin/ethtool -a"
        actual = self.spec.get_for_uploader()
        self.assertEqual(expected, actual)

    def test_get_regex(self):
        actual = self.spec.get_regex().pattern
        expected = '.*/' + self.spec.get_path() + "$"
        self.assertEqual(expected, actual)

    def test_get_preferred_path(self):
        self.assertEqual(self.spec.get_preferred_path(), self.spec.get_regex())


class TestRelativePathCommandSpec(unittest.TestCase):

    def test_relative_path_raises_specpatherror(self):
        with self.assertRaises(SpecPathError):
            self.spec = CommandSpec('ls -la')


class TestInsightsDataSpecConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.static_specs = {
            "nproc.conf": PatternSpec(r"etc/security/limits\.d/.*-nproc\.conf"),
            "blkid": CommandSpec("/usr/sbin/blkid -c /dev/null"),
            "bond": PatternSpec(r"proc/net/bonding/bond.*"),
            "chkconfig": CommandSpec("/sbin/chkconfig --list"),
            "dmesg": CommandSpec("/bin/dmesg", large_content=True),
            "ethtool-a": CommandSpec("/sbin/ethtool -a {iface}", iface=r"\S+"),
            "installed-rpms": First([CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(), multi_output=False),
                                     CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(1), multi_output=False),
                                     CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(3), multi_output=False)]),
            "multiple-rpms": All([CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(), multi_output=False),
                                  CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(1), multi_output=False),
                                  CommandSpec("/bin/rpm -qa --qf='%s'" % format_rpm(3), multi_output=False)]),
            "docker_image_inspect": DockerHostCommandSpec("/usr/bin/docker inspect --type=image {DOCKER_IMAGE_NAME}"),
        }

        cls.meta_files = {
            "machine-id": SimpleFileSpec("etc/redhat-access-insights/machine-id"),
            "branch_info": SimpleFileSpec("branch_info"),
            "uploader_log": SimpleFileSpec("var/log/redhat-access-insights/redhat-access-insights.log")
        }

        cls.inconsistent_specs = {
            "dumpe2fs-h": All([CommandSpec("/sbin/dumpe2fs -h {dumpdev}", dumpdev=r"\S+"),
                               CommandSpec("/usr/sbin/dumpe2fs")]),
        }

        cls.additional_specs = {
            "installed-rpms": SimpleFileSpec("installed-rpms")
        }

        cls.config = InsightsDataSpecConfig(cls.static_specs, cls.meta_files)

    def test_inconsistent_specs(self):
        with pytest.raises(Exception):
            InsightsDataSpecConfig(self.inconsistent_specs, self.meta_files)

    def test_additional_specs(self):
        my_config = InsightsDataSpecConfig(self.static_specs, self.meta_files)
        my_config.merge(group_wrap(self.additional_specs))
        self.assertEqual(my_config.get_spec_list('installed-rpms')[-1],
                         self.additional_specs["installed-rpms"])

    def test_iteritems(self):
        for k, v in self.config.iteritems():
            self.assertEqual(v.get_all_specs(), self.config.get_spec_list(k))

    def test_get_spec_list(self):
        actual = self.config.get_spec_list('blkid')[0]
        expected = self.static_specs.get('blkid')
        self.assertEqual(expected, actual)

    def test_get_spec_list_multi(self):
        actual = self.config.get_spec_list('installed-rpms')
        expected = self.static_specs.get('installed-rpms').get_all_specs()
        self.assertEqual(expected, actual)
        self.assertEqual(len(actual), 3)

    def test_specgroup_all(self):
        actual = len(self.config.get_specs('multiple-rpms'))
        expected = len(self.static_specs.get('multiple-rpms').get_specs())
        self.assertEqual(expected, actual)
        self.assertEqual(actual, 3)

    def test_get_meta_spec_list(self):
        actual = self.config.get_meta_spec_list('machine-id')
        expected = self.meta_files.get('machine-id')
        self.assertEqual([expected], actual)

    def test_is_large(self):
        self.assertFalse(self.config.is_large('blkid'))
        self.assertFalse(self.config.is_large('bond'))
        self.assertFalse(self.config.is_large('installed-rpms'))
        self.assertTrue(self.config.is_large('dmesg'))

    def test_is_multi_output(self):
        self.assertFalse(self.config.is_multi_output('90-nproc.conf'))
        self.assertFalse(self.config.is_multi_output('installed-rpms'))
        self.assertTrue(self.config.is_multi_output('bond'))
        self.assertTrue(self.config.is_multi_output('ethtool-a'))
        self.assertFalse(self.config.is_multi_output('dmesg'))

    def test_max_line_size(self):
        self.assertTrue(self.config.max_line_size() > 0)

    def check_spec_archive2regex(self, spec_name, analysis_target):
        #    check that the filename returned by get_archive_file_name
        #    can be matched by the regex returned by get_regex
        spec = self.config.get_specs(spec_name)[0]
        name_in_archive = spec.get_archive_file_name(analysis_target=analysis_target)
        if spec.get_pre_command_key():
            name_in_archive += "ArbitraryNonBlankCharacters"
        for v in CommandSpec.CLIENT_SIDE_VARIABLES:
            name_in_archive = name_in_archive.replace("{%s}" % v, "ArbitraryNonBlankCharacters")
        regex = spec.get_regex(prefix=".*", suffix=r"$", analysis_target=analysis_target)
        self.assertRegexpMatches(name_in_archive, regex)

    def test_commandspec(self):
        self.check_spec_archive2regex('chkconfig', HostTarget.instance)

    def test_rpmspec(self):
        self.check_spec_archive2regex('installed-rpms', HostTarget.instance)
        self.check_spec_archive2regex('installed-rpms', DockerImageTarget.instance)
        self.check_spec_archive2regex('installed-rpms', DockerContainerTarget.instance)

    def test_multispec(self):
        self.check_spec_archive2regex('ethtool-a', HostTarget.instance)

    def test_client_variable(self):
        self.check_spec_archive2regex('docker_image_inspect', DockerImageTarget.instance)


class TestRetargetCommand(unittest.TestCase):

    sh_join_test_data = [
        "ls this is\ a \"test of the emergency\"",
        "ls this is\ \ \ a \"test of the emergency\"",
        "ls te\\\"st",
        "ls te\\\'st",
        "ls te\\\\st",
        "ls te\\\'\\\'st",
        "ls te\\\'\\\'\\\'st",
        "ls te\\\"\\\\\\\'st",
        "ls te\\\"\\\'\\\\st",
        "ls \"this \\\"is a\\\" test\"",
    ]

    def test_retarget_command_for_mountpoint_1(self):
        for each in self.sh_join_test_data:
            self.assertEqual(shlex.split(each), shlex.split(sh_join(shlex.split(each))))

    retarget_test_data = [
        ("/usr/bin/yum -C repolist", "/usr/bin/yum --installroot={CONTAINER_MOUNT_POINT} -C repolist"),
        ("/bin/rpm -qa --qf='%s'" % format_rpm(3), "/bin/rpm --root={CONTAINER_MOUNT_POINT} -qa --qf='%s'" % format_rpm(3)),
        ("/bin/date", "/bin/date"),
        ("systemctl list-unit-files", "systemctl --root={CONTAINER_MOUNT_POINT} list-unit-files"),
        (r"/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report'", r"/usr/bin/find {CONTAINER_MOUNT_POINT}/var/crash {CONTAINER_MOUNT_POINT}/var/tmp -path '*.reports-*/whoopsie-report'"),
        (r"/usr/bin/find -H /var/crash /var/tmp -path '*.reports-*/whoopsie-report'", r"/usr/bin/find -H {CONTAINER_MOUNT_POINT}/var/crash {CONTAINER_MOUNT_POINT}/var/tmp -path '*.reports-*/whoopsie-report'"),
        ("/sbin/lsmod", None),
        ("/usr/bin/ls -lanR /dev", "/usr/bin/ls -lanR {CONTAINER_MOUNT_POINT}/dev"),
        ("/usr/bin/ls -l /boot/grub2/grub.cfg", "/usr/bin/ls -l {CONTAINER_MOUNT_POINT}/boot/grub2/grub.cfg"),
    ]

    def test_retarget_command_for_mountpoint_2(self):
        for each in self.retarget_test_data:
            retargeted_command = retarget_command_for_mountpoint(each[0])
            expected_retargeted_command = each[1]
            if expected_retargeted_command is None:
                self.assertEqual(retargeted_command, expected_retargeted_command)
            else:
                self.assertEqual(shlex.split(retargeted_command),
                                 shlex.split(expected_retargeted_command))
