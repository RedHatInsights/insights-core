"""
NormalMD5 Combiner for the NormalMD5 Parser
===========================================

Combiner for the :class:`insights.parsers.md5check.NormalMD5` parser.

This parser is multioutput, one parser instance for each file md5sum.
Ths combiner puts all of them back together and presents them as a dict
where the keys are the filenames and the md5sums are the values.

This class inherits all methods and attributes from the ``dict`` object.

Examples:
    >>> type(md5sums)
    <class 'insights.combiners.md5check.NormalMD5'>
    >>> sorted(md5sums.keys())
    ['/etc/localtime1', '/etc/localtime2']
    >>> md5sums['/etc/localtime2']
    'd41d8cd98f00b204e9800998ecf8427e'
"""

from .. import combiner
from insights.parsers.md5check import NormalMD5 as NormalMD5Parser


@combiner(NormalMD5Parser)
class NormalMD5(dict):
    """
    Combiner for the NormalMD5 parser.
    """
    def __init__(self, md5_checksums):
        super(NormalMD5, self).__init__()
        for md5info in md5_checksums:
            self.update({md5info.filename: md5info.md5sum})
