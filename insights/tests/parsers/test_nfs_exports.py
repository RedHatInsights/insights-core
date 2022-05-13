from insights.parsers import nfs_exports as parsermodule
from insights.parsers.nfs_exports import NFSExports, NFSExportsD
from insights.tests import context_wrap
from doctest import testmod

EXPORTS = """
/home/utcs/shared/ro                    @group(ro,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
/home/insights/shared/rw                @group(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)
/home/insights/shared/special/all/mail  @group(rw,sync,no_root_squash)
/home/insights/ins/special/all/config   @group(ro,sync,no_root_squash)  ins1.example.com(rw,sync,no_root_squash)
#/home/insights                          ins1.example.com(rw,sync,no_root_squash)
/home/example                           @group(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
# A duplicate host for this exported path
/home/example                           ins2.example.com(rw,sync,no_root_squash)
"""


def test_module_documentation():
    failed, total = testmod(parsermodule, globs={
        "exports": NFSExports(context_wrap(EXPORTS))
    })
    assert failed == 0


def test_nfs_exports():
    nfs_exports = NFSExports(context_wrap(EXPORTS))
    _do(nfs_exports)


def test_nfs_exports_d():
    nfs_exports = NFSExportsD(context_wrap(EXPORTS))
    _do(nfs_exports)


def test_nfs_exports_empty():
    nfs_exports = NFSExports(context_wrap(""))
    _do_empty(nfs_exports)


def test_nfs_exports_d_empty():
    nfs_exports = NFSExportsD(context_wrap(""))
    _do_empty(nfs_exports)


def _do_empty(nfs_exports):
    assert nfs_exports.data == {}
    assert nfs_exports.ignored_exports == {}
    assert nfs_exports.raw_lines == {}
    assert nfs_exports.all_options() == set()
    assert nfs_exports.export_paths() == set()


def _do(nfs_exports):
    assert nfs_exports.data == {
        "/home/utcs/shared/ro": {
            "@group": ["ro", "sync"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["rw", "sync", "no_root_squash"]
        }, "/home/insights/shared/rw": {
            "@group": ["rw", "sync"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["ro", "sync", "no_root_squash"]
        }, "/home/insights/shared/special/all/mail": {
            "@group": ["rw", "sync", "no_root_squash"]
        }, "/home/insights/ins/special/all/config": {
            "@group": ["ro", "sync", "no_root_squash"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"]
        }, "/home/example": {
            "@group": ["rw", "sync", "root_squash"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["rw", "sync", "no_root_squash"]
        }
    }

    assert nfs_exports.ignored_exports == {
        '/home/example': {'ins2.example.com': ['rw', 'sync', 'no_root_squash']}
    }

    assert nfs_exports.raw_lines == {
        "/home/utcs/shared/ro": [
            '/home/utcs/shared/ro                    @group(ro,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)'
        ], "/home/insights/shared/rw": [
            '/home/insights/shared/rw                @group(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)'
        ], "/home/insights/shared/special/all/mail": [
            '/home/insights/shared/special/all/mail  @group(rw,sync,no_root_squash)'
        ], "/home/insights/ins/special/all/config": [
            '/home/insights/ins/special/all/config   @group(ro,sync,no_root_squash)  ins1.example.com(rw,sync,no_root_squash)'
        ], "/home/example": [
            '/home/example                           @group(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)',
            '/home/example                           ins2.example.com(rw,sync,no_root_squash)'
        ]
    }

    assert nfs_exports.all_options() == set(["ro", "rw", "sync", "no_root_squash", "root_squash"])
    assert nfs_exports.export_paths() == set([
        "/home/utcs/shared/ro", "/home/insights/shared/rw",
        "/home/insights/shared/special/all/mail",
        "/home/insights/ins/special/all/config", "/home/example"
    ])


def test_reconstitute():
    # This is deprecated and will be removed in the future and is here for
    # testing completeness.
    recon = NFSExports.reconstitute(
        "/home/utcs/shared/ro", {
            "@group": ["ro", "sync"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["rw", "sync", "no_root_squash"]
        }
    )
    # Because reconstitute uses iteritems, we can't test the order
    # definitively.  We have to check that it's included each host definition.
    assert recon.startswith('/home/utcs/shared/ro')
    for host in ('@group', 'ins1.example.com', 'ins2.example.com'):
        assert ' ' + host + '(' in recon


NFS_EXPORTS_CORNER_CASES = '''
# Host with default share options
/mnt/share      host1
# Export with two non-overlapping host definitions
/mnt/share      host2(rw)
# No matter how many times a host is listed, only the first gets picked up
/mnt/share      host2(ro)
# Need to list on separate lines because of dictionary key merging
/mnt/share      host2(no_root_squash)
'''


def test_nfs_exports_corner_cases():
    exports = NFSExports(context_wrap(NFS_EXPORTS_CORNER_CASES))
    assert exports

    assert exports.data['/mnt/share'] == {'host1': [], 'host2': ['rw']}
    # Note: only the last ignored export gets stored per host.
    assert exports.ignored_exports['/mnt/share'] == {'host2': ['no_root_squash']}
    for path, hosts in exports:
        assert path in exports.data
        assert exports.data[path] == hosts
