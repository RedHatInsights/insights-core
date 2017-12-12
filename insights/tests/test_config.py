import pytest
import shlex

from insights.config import InsightsDataSpecConfig, SimpleFileSpec, PatternSpec, CommandSpec, format_rpm, All, First, group_wrap
from insights.config import DockerHostCommandSpec, SpecPathError, SpecSyntaxError
from insights.util.command import retarget_command_for_mountpoint, sh_join
from insights.config import HostTarget, DockerImageTarget, DockerContainerTarget


DUMMY_PATH = r'path/to/thing'
WITH_DOLLAR = DUMMY_PATH + r'$'


@pytest.fixture
def simple_spec():
    return SimpleFileSpec(DUMMY_PATH)


def test_absolute_path_raises_specpatherror():
    with pytest.raises(SpecPathError):
        SimpleFileSpec('/etc/php.ini')


def test_get_path(simple_spec):
    assert DUMMY_PATH == simple_spec.get_path()


def test_get_regex(simple_spec):
    assert WITH_DOLLAR == simple_spec.get_regex().pattern


def test_get_regex_prefix(simple_spec):
    prefix = 'prefix'
    assert prefix + WITH_DOLLAR == simple_spec.get_regex(prefix=prefix).pattern


def test_get_regex_suffix(simple_spec):
    suffix = 'suffix'
    assert DUMMY_PATH + suffix == simple_spec.get_regex(suffix=suffix).pattern


def test_get_preferred_path(simple_spec):
    with pytest.raises(NotImplementedError):
        simple_spec.get_preferred_path()


def test_default_is_multi_output(simple_spec):
    assert not simple_spec.is_multi_output()


def test_default_is_large(simple_spec):
    assert not simple_spec.is_large()


def test_get_dynamic_args(simple_spec):
    assert simple_spec.get_dynamic_args() == []


@pytest.fixture
def pattern_spec():
    return PatternSpec(DUMMY_PATH)


def test_pattern_default_is_multi_output(pattern_spec):
    assert pattern_spec.is_multi_output()


def test_pattern_default_is_large(pattern_spec):
    assert not pattern_spec.is_large()


def test_matches(pattern_spec):
    assert pattern_spec.matches('/path/to/thing')
    assert not pattern_spec.matches('/some/other/path')


@pytest.fixture
def command_spec():
    return CommandSpec("/sbin/ethtool -a {iface}", iface=r"\S+")


def test_string_representation(command_spec):
    assert command_spec.__str__() is not None


def test_command_default_is_multi_output(command_spec):
    assert command_spec.is_multi_output()


def test_command_default_is_large(command_spec):
    assert not command_spec.is_large()


def test_mangle_name():
    command = "/sbin/ethtool -a"
    expected = 'ethtool_-a'
    actual = CommandSpec.mangle_command(command)
    assert expected == actual


def test_get_path_multi_output(command_spec):
    actual = command_spec.get_path()
    expected = 'ethtool_-a_(?P<iface>\\S+)'
    assert expected == actual


def test_get_path_context_dict(command_spec):
    match = command_spec.get_regex().match("stuff/ethtool_-a_eth0")
    actual = match.groupdict()
    expected = {"iface": "eth0"}
    assert expected == actual


def test_get_path_non_multi_output():
    command_string = "/sbin/ethtool -a"
    spec = CommandSpec(command_string)
    actual = spec.get_path()
    expected = 'ethtool_-a'
    assert expected == actual


def test_get_for_uploader_non_multi_output():
    command_string = "/sbin/ethtool -a"
    spec = CommandSpec(command_string)
    actual = spec.get_for_uploader()
    assert command_string == actual


def test_get_for_uploader_multi_output(command_spec):
    expected = "/sbin/ethtool -a"
    actual = command_spec.get_for_uploader()
    assert expected == actual


def test_command_get_regex(command_spec):
    actual = command_spec.get_regex().pattern
    expected = '.*/' + command_spec.get_path() + "$"
    assert expected == actual


def test_command_get_preferred_path(command_spec):
    assert command_spec.get_preferred_path() == command_spec.get_regex()


def test_relative_path_raises_specpatherror():
    with pytest.raises(SpecPathError):
        CommandSpec('ls -la')


def test_shellism_raises_specpatherror():
    with pytest.raises(SpecSyntaxError) as e:
        assert not CommandSpec('/bin/find /etc -name *.xml | grep Tomcat >/dev/null && echo Foo')
    assert 'Shell directive && found in command as the start of a word - this is not executed by a shell' in str(e)


def test_quoted_shellism_is_ok():
    spec = CommandSpec("/sbin/lvs -s '|'")
    assert spec.get_path() == 'lvs_-s'


def test_internal_shellism_is_ok():
    spec = CommandSpec("/sbin/lvs --separator=|")
    assert spec.get_path() == 'lvs_--separator'


@pytest.fixture
def static_specs():
    return {
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


@pytest.fixture
def meta_files():
    return {
        "machine-id": SimpleFileSpec("etc/redhat-access-insights/machine-id"),
        "branch_info": SimpleFileSpec("branch_info"),
        "uploader_log": SimpleFileSpec("var/log/redhat-access-insights/redhat-access-insights.log")
    }


@pytest.fixture
def inconsistent_specs():
    return {
        "dumpe2fs-h": All([CommandSpec("/sbin/dumpe2fs -h {dumpdev}", dumpdev=r"\S+"),
                           CommandSpec("/usr/sbin/dumpe2fs")]),
    }


@pytest.fixture
def additional_specs():
    return {
        "installed-rpms": SimpleFileSpec("installed-rpms")
    }


@pytest.fixture
def config():
    return InsightsDataSpecConfig(static_specs(), meta_files())


def test_inconsistent_specs(inconsistent_specs, meta_files):
    with pytest.raises(Exception):
        InsightsDataSpecConfig(inconsistent_specs, meta_files)


def test_additional_specs(static_specs, meta_files, additional_specs):
    my_config = InsightsDataSpecConfig(static_specs, meta_files)
    my_config.merge(group_wrap(additional_specs))
    assert my_config.get_spec_list('installed-rpms')[-1] == additional_specs["installed-rpms"]


def test_iteritems(config):
    for k, v in config.iteritems():
        assert v.get_all_specs() == config.get_spec_list(k)


def test_get_spec_list(static_specs, config):
    actual = config.get_spec_list('blkid')[0]
    expected = static_specs.get('blkid')
    assert expected == actual


def test_get_spec_list_multi(static_specs, config):
    actual = config.get_spec_list('installed-rpms')
    expected = static_specs.get('installed-rpms').get_all_specs()
    assert expected == actual
    assert len(actual) == 3


def test_specgroup_all(static_specs, config):
    actual = len(config.get_specs('multiple-rpms'))
    expected = len(static_specs.get('multiple-rpms').get_specs())
    assert expected == actual
    assert actual == 3


def test_get_meta_spec_list(config, meta_files):
    actual = config.get_meta_spec_list('machine-id')
    expected = meta_files.get('machine-id')
    assert [expected] == actual


def test_is_large(config):
    for i in ('blkid', 'bond', 'installed-rpms'):
        assert not config.is_large(i)
    assert config.is_large('dmesg')


def test_is_multi_output(config):
    for i in ('90-nproc.conf', 'installed-rpms', 'dmesg'):
        assert not config.is_multi_output(i)
    for i in ('bond', 'ethtool-a'):
        assert config.is_multi_output(i)


def test_max_line_size(config):
    assert config.max_line_size() > 0


def check_spec_archive2regex(config, spec_name, analysis_target):
    #    check that the filename returned by get_archive_file_name
    #    can be matched by the regex returned by get_regex
    spec = config.get_specs(spec_name)[0]
    name_in_archive = spec.get_archive_file_name(analysis_target=analysis_target)
    if spec.get_pre_command_key():
        name_in_archive += "ArbitraryNonBlankCharacters"
    for v in CommandSpec.CLIENT_SIDE_VARIABLES:
        name_in_archive = name_in_archive.replace("{%s}" % v, "ArbitraryNonBlankCharacters")
    regex = spec.get_regex(prefix=".*", suffix=r"$", analysis_target=analysis_target)
    assert regex.search(name_in_archive)


def test_commandspec(config):
    check_spec_archive2regex(config, 'chkconfig', HostTarget.instance)


def test_rpmspec(config):
    check_spec_archive2regex(config, 'installed-rpms', HostTarget.instance)
    check_spec_archive2regex(config, 'installed-rpms', DockerImageTarget.instance)
    check_spec_archive2regex(config, 'installed-rpms', DockerContainerTarget.instance)


def test_multispec(config):
    check_spec_archive2regex(config, 'ethtool-a', HostTarget.instance)


def test_client_variable(config):
    check_spec_archive2regex(config, 'docker_image_inspect', DockerImageTarget.instance)


SH_JOIN_TEST_DATA = [
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


def test_retarget_command_for_mountpoint_1():
    for each in SH_JOIN_TEST_DATA:
        assert shlex.split(each) == shlex.split(sh_join(shlex.split(each)))


RETARGET_TEST_DATA = [
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


def test_retarget_command_for_mountpoint_2():
    for each in RETARGET_TEST_DATA:
        retargeted_command = retarget_command_for_mountpoint(each[0])
        expected_retargeted_command = each[1]
        if expected_retargeted_command is None:
            assert retargeted_command == expected_retargeted_command
        else:
            assert shlex.split(retargeted_command) == shlex.split(expected_retargeted_command)
