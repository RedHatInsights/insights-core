from insights.parsers.nfs_exports import NFSExports, NFSExportsD
from insights.parsers.tests.test_nfs_exports import EXPORTS
from insights.combiners import nfs_exports
from insights.tests import context_wrap

from doctest import testmod

EXPORTS_D_EXTRAS = """
/mnt/work       *(rw,sync)
/mnt/backup     10.0.0.0/24(rw,sync,no_root_squash)
# We expect the following to be stored in the ignored_exports property
# as it has a duplicate host declaration for this path.
/home/insights/shared/rw ins1.redhat.com(rw,sync,no_root_squash)
"""

# Set up combined test environment for docs and for more thorough functional
# testing.
nfs_exportsf = NFSExports(
    context_wrap(EXPORTS, path="/etc/exports")
)
nfs_exportsd = [NFSExportsD(
    context_wrap(EXPORTS_D_EXTRAS, path="/etc/exports.d/mnt.exports")
)]
combined = nfs_exports.AllNFSExports(nfs_exportsf, nfs_exportsd)


def test_nfs_exports_docs():
    failed, total = testmod(nfs_exports, globs={'all_nfs': combined})
    assert failed == 0


def test_nfs_export_combiner():
    assert combined
    assert hasattr(combined, 'exports')
    assert isinstance(combined.exports, dict)
    assert combined.exports
    assert len(combined.exports) == 7
    assert sorted(combined.exports.keys()) == sorted([
        '/home/utcs/shared/ro', '/home/insights/shared/rw',
        '/home/insights/shared/special/all/mail',
        '/home/insights/ins/special/all/config', '/home/redhat', '/mnt/work',
        '/mnt/backup'
    ])
    for path, hosts in nfs_exportsf.data.iteritems(:
        assert hosts == combined.exports[path]

    assert hasattr(combined, 'ignored_exports')
    assert isinstance(combined.ignored_exports, dict)
    assert combined.ignored_exports
    assert len(combined.ignored_exports) == 2
    print combined.ignored_exports.keys()
    assert sorted(combined.ignored_exports.keys()) == sorted([
        '/home/insights/shared/rw', '/home/redhat'
    ])

    assert hasattr(combined, 'raw_lines')
    assert isinstance(combined.raw_lines, dict)
    assert combined.raw_lines
