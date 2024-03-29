"""
VersionInfo - file ``version_info``
===================================

.. warning::
    This parser is deprecated, please use
    :py:class:`insights.parsers.client_metadata.VersionInfo` instead.


The version of the insights core and insights client that the archive used.
"""
from insights import JSONParser, parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.version_info)
class VersionInfo(JSONParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.client_metadata.VersionInfo` instead.

    This parser parses the ``version_info`` file generated by the
    ``insights-client`` command.

    Typical content of this file is::

        {"core_version": "3.0.203-1", "client_version": "3.1.1"}

    .. note::

        The :attr:`client_version` provided by this Parser is a short version
        only, to get the full version of the ``insights-client`` package,
        please use the :class:`insights.parsers.installed_rpms.InstalledRpms`
        Parser instead.

    Examples:
        >>> ver.core_version == '3.0.203-1'
        True
        >>> ver.client_version == '3.1.1'
        True
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            VersionInfo,
            "Please use insights.parsers.client_metadata.VersionInfo instead.",
            "3.4.0"
        )
        super(VersionInfo, self).__init__(*args, **kwargs)

    @property
    def core_version(self):
        """
        Returns:
            (str): The version of the insights core.
        """
        return self.data['core_version']

    @property
    def client_version(self):
        """
        Returns:
            (str): The version of the insights client.

        .. note::

            This attribute returns a short version of the insights client only,
            to get the full version of the ``insights-client`` package, please
            use the :class:`insights.parsers.installed_rpms.InstalledRpms` Parser
            instead.
        """
        return self.data['client_version']
