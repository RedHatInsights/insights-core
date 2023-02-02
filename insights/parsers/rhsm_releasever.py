"""
RHSM Release Version - ``file /var/lib/rhsm/cache/releasever.json``
===================================================================
Parser Red Hat Subscription manager release info.

"""
from insights.core import JSONParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.rhsm_releasever)
class RhsmReleaseVer(JSONParser):
    """
    Class for parsing the file: ``/var/lib/rhsm/cache/releasever.json``.

    This information mirror the information provided by the
    ``subscription-manager release --show`` command.

    .. note::
        Please refer to the super-class :class:`insights.core.JSONParser`
        for additional information on attributes and methods.

    Sample input data::

        {"releaseVer": "6.10"}

    Raises:
       SkipComponent: When the json content of the file is empty.(i.e release version is empty. eg. {})

    Examples:
        >>> type(rhsm_releasever)
        <class 'insights.parsers.rhsm_releasever.RhsmReleaseVer'>
        >>> rhsm_releasever['releaseVer'] == '6.10'
        True
        >>> rhsm_releasever.set == '6.10'
        True
        >>> rhsm_releasever.major
        6
        >>> rhsm_releasever.minor
        10
    """

    def parse_content(self, content):
        """
        Parse the contents of file ``/var/lib/rhsm/cache/releasever.json``.
        """
        super(RhsmReleaseVer, self).parse_content(content)
        self.set = self.major = self.minor = None
        if 'releaseVer' not in self.data:
            raise SkipComponent('releaseVer is not in data')
        rel = self.data.get('releaseVer') or ''
        rel_splits = rel.split('.')
        # Release: 6.7
        if len(rel_splits) == 2:
            if rel_splits[0].isdigit() and rel_splits[-1].isdigit():
                self.set = rel
                self.major = int(rel_splits[0])
                self.minor = int(rel_splits[-1])

        # Release: 7Server or 8
        elif rel and rel[0].isdigit():
            self.set = rel
            self.major = int(rel[0])
            # leave self.minor as None
