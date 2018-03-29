from insights.parsers.nfs_exports import NFSExports, NFSExportsD
from insights.tests import context_wrap

EXPORTS = """
/home/utcs/shared/ro @rhtttttttttttt(ro,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
/home/insights/shared/rw @rhtttttttttttt(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)
/home/insights/shared/special/all/mail   @rhtttttttttttt(rw,sync,no_root_squash)
/home/insights/ins/special/all/config   @rhtttttttttttt(ro,sync,no_root_squash)  ins1.example.com(rw,sync,no_root_squash)
#/home/insights ins1.example.com(rw,sync,no_root_squash)
/home/example           @rhtttttttttttt(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
/home/example           ins3.example.com(rw,sync,no_root_squash)
""".strip()


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
    assert nfs_exports.ignored_lines == []
    assert nfs_exports.all_options() == set()
    assert nfs_exports.export_paths() == set()


def _do(nfs_exports):
    assert nfs_exports.data == {
        "/home/utcs/shared/ro": {
            "@rhtttttttttttt": ["ro", "sync"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["rw", "sync", "no_root_squash"]
        }, "/home/insights/shared/rw": {
            "@rhtttttttttttt": ["rw", "sync"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["ro", "sync", "no_root_squash"]
        }, "/home/insights/shared/special/all/mail": {
            "@rhtttttttttttt": ["rw", "sync", "no_root_squash"]
        }, "/home/insights/ins/special/all/config": {
            "@rhtttttttttttt": ["ro", "sync", "no_root_squash"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"]
        }, "/home/example": {
            "@rhtttttttttttt": ["rw", "sync", "root_squash"],
            "ins1.example.com": ["rw", "sync", "no_root_squash"],
            "ins2.example.com": ["rw", "sync", "no_root_squash"]
        }
    }
    assert nfs_exports.ignored_lines == [
        "/home/example           ins3.example.com(rw,sync,no_root_squash)"
    ]
    assert nfs_exports.all_options() == set(["ro", "rw", "sync", "no_root_squash", "root_squash"])
    assert nfs_exports.export_paths() == set([
        "/home/utcs/shared/ro", "/home/insights/shared/rw",
        "/home/insights/shared/special/all/mail",
        "/home/insights/ins/special/all/config", "/home/example"
    ])
