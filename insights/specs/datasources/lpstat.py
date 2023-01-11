"""
Custom datasources for lpstat information
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by lpstat datasources """

    lpstat_v = simple_command("/usr/bin/lpstat -v")
    """ Returns the output of command ``/usr/bin/lpstat -v`` """


@datasource(LocalSpecs.lpstat_v, HostContext)
def lpstat_protocol_printers_info(broker):
    """
    This datasource provides the not-sensitive information collected
    from ``/usr/bin/lpstat -v``.

    Typical content of ``/usr/bin/lpstat -v`` file is::

        "device for test_printer1: ipp://cups.test.com/printers/test_printer1"

    Returns:
        DatasourceProvider: Returns the collected content containing non-sensitive information

    Raises:
        SkipComponent: When the filter/path does not exist or any exception occurs.
    """
    try:
        content = broker[LocalSpecs.lpstat_v].content
        result = []
        for line in content:
            if "device for " in line:
                "Remove printer address information"
                result.append(line.split("://", 1)[0] if '://' in line else line)
        if result:
            return DatasourceProvider(content="\n".join(result), relative_path='insights_commands/lpstat_-v')
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
