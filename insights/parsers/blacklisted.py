"""
BlacklistedSpecs - File ``blacklisted_specs``
=============================================
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.blacklisted_specs)
class BlacklistedSpecs(JSONParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.client_metadata.BlacklistedSpecs` instead.

    Parses the "blacklisted_specs" or "blacklisted_specs.txt" file generated
    on archive creation.

    Typical output::
        "{"specs": ["dmesg", "fstab"]}"

    Attributes:
        specs (list): List of blacklisted specs.

    Examples:
        >>> type(specs)
        <class 'insights.parsers.blacklisted.BlacklistedSpecs'>
        >>> result = ['dmesg', 'fstab']
        >>> specs.specs == result
        True
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            BlacklistedSpecs,
            "Please use insights.parsers.client_metadata.BlacklistedSpecs instead.",
            "3.3.25"
        )
        super(BlacklistedSpecs, self).__init__(*args, **kwargs)

    @property
    def specs(self):
        return self.data['specs']
