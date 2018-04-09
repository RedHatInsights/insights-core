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
