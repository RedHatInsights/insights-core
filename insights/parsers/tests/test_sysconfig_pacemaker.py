from insights.tests import context_wrap
from insights.parsers.sysconfig import PacemakerSysconfig

PACEMAKER = """
# Set as for PCMK_debug above to run some or all daemons under valgrind with
# the callgrind tool enabled.
# PCMK_callgrind_enabled=no

# Set the options to pass to valgrind, when valgrind is enabled. See
# valgrind(1) man page for details. "--vgdb=no" is specified because
# pacemaker-execd can lower privileges when executing commands, which would
# otherwise leave a bunch of unremovable files in /tmp.
VALGRIND_OPTS="--leak-check=full --trace-children=no --vgdb=no --num-callers=25 --log-file=/var/lib/pacemaker/valgrind-%p --suppressions=/usr/share/pacemaker/tests/valgrind-pcmk.suppressions --gen-suppressions=all"
""".strip()


def test_sysconfig_pacemaker():
    result = PacemakerSysconfig(context_wrap(PACEMAKER))
    assert 'PCMK_callgrind_enabled' not in result
    assert result.get('PCMK_callgrind_enabled') is None
    assert 'VALGRIND_OPTS' in result
    assert result['VALGRIND_OPTS'] == '--leak-check=full --trace-children=no --vgdb=no --num-callers=25 --log-file=/var/lib/pacemaker/valgrind-%p --suppressions=/usr/share/pacemaker/tests/valgrind-pcmk.suppressions --gen-suppressions=all'
    assert result.get('VALGRIND_OPTS') == '--leak-check=full --trace-children=no --vgdb=no --num-callers=25 --log-file=/var/lib/pacemaker/valgrind-%p --suppressions=/usr/share/pacemaker/tests/valgrind-pcmk.suppressions --gen-suppressions=all'
