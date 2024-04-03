from mock.mock import patch

from insights import dr
from insights.collect import apply_blacklist
from insights.core import blacklist


def setup_function(func):
    if func is test_apply_blacklist_valid:
        dr.load_components('insights.specs.default.DefaultSpecs')


@patch('insights.collect.log.warning')
def test_apply_blacklist_valid(_log):
    rm_conf = {
        'commands':
            [
                # simple_command
                "/bin/df -alP -x autofs",
                "/bin/ps aux",
                # foreach_execute
                "/bin/du -s -k",
                # command_with_args
                "/usr/bin/getent group",
                # spec name
                "installed_rpms",  # will be converted to component
            ],
        'files':
            [
                # simple_file
                "/var/log/messages",
                # first_file
                "/proc/meminfo",
                # glob_file
                "/boot/config-",
                # spec name
                "container_installed_rpms",  # will be converted to component
            ],
        'components':
            [
                "insights.specs.default.DefaultSpecs.parted__l",
            ]
    }

    apply_blacklist(rm_conf)

    # components
    assert dr.is_enabled('insights.specs.default.DefaultSpecs.uname') is True
    expected_comp = ['installed_rpms', 'container_installed_rpms', 'parted__l']
    for exp in expected_comp:
        assert exp in blacklist.BLACKLISTED_SPECS
        comp_name = 'insights.specs.default.DefaultSpecs.{0}'.format(exp)
        comp = dr.get_component_by_name(comp_name)
        assert dr.is_enabled(comp) is False
        _log.assert_any_call("WARNING: Skipping component: %s" % comp_name)

    # files
    check_files = rm_conf['files'][:-1]
    for fil in check_files:
        assert blacklist.allow_file(fil) is False
        _file = fil + ' abc'
        assert blacklist.allow_file(_file) is False
        _file = fil + 'abc'
        assert blacklist.allow_file(_file) is True

    # commonds
    check_commands = rm_conf['commands'][:-1]
    for cmd in check_commands:
        assert blacklist.allow_command(cmd) is False
        _cmd = cmd + ' abc'
        assert blacklist.allow_command(_cmd) is False
        _cmd = cmd + 'abc'
        assert blacklist.allow_command(_cmd) is True


@patch('insights.collect.log.warning')
def test_apply_blacklist_invalid(_log):
    rm_conf = {'commands': ["test1", "/usr/bin/test"],
               'files': ["test2", "/etc/test"],
               'components': ['insights.specs.default.DefaultSpecs.test']}

    apply_blacklist(rm_conf)

    # components
    unknow_comp = rm_conf['components'][0]
    _log.assert_any_call("WARNING: Unknown component in blacklist: %s" % unknow_comp)

    # files
    expected_file = rm_conf['files']
    for exp in expected_file:
        assert blacklist.allow_file(exp) is False

    # commands
    expected_file = rm_conf['commands']
    for exp in expected_file:
        assert blacklist.allow_command(exp) is False


@patch('insights.collect.log.warning')
def test_apply_blacklist_empty(_log):
    rm_conf = {}
    apply_blacklist(rm_conf)
    _log.assert_not_called()
