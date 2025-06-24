from insights.core.ls_parser import FilePermissions as FP
from insights.util import deprecated


class FilePermissions(FP):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.core.ls_parser.FilePermissions` instead.
    """

    def __init__(self, *args, **kwargs):
        deprecated(
            FilePermissions, "Please use insights.core.ls_parser.FilePermissions instead.", "3.7.0"
        )
        super(FilePermissions, self).__init__(*args, **kwargs)
