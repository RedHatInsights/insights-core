from insights.core import YAMLParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.branch_info)
class BranchInfo(YAMLParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.client_metadata.BranchInfo` instead.

    Class for parsing the content of ``branch_info``.
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            BranchInfo,
            "Please use insights.parsers.client_metadata.BranchInfo instead.",
            "3.4.0"
        )
        super(BranchInfo, self).__init__(*args, **kwargs)
