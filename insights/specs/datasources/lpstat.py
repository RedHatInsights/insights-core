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


class LocalSpecsLpstatO(Specs):
    """ Local specs used only by ethernet.interfaces datasource. """
    lpstat_o = simple_command("/usr/bin/lpstat -o")


@datasource(LocalSpecsLpstatO.lpstat_o, HostContext)
def lpstat_queued_jobs_number(broker):
    """
    This datasource provides the number of all queued job.

    Typical content of ``/usr/bin/lpstat -o`` file is::

        Cups-PDF-1802           root          265443328   Tue 05 Sep 2023 02:21:19 PM CST
        Cups-PDF-1803           root          265443328   Tue 05 Sep 2023 02:21:21 PM CST
        Cups-PDF-1804           root          265443328   Tue 05 Sep 2023 02:21:22 PM CST
        Cups-PDF-1805           root          265443328   Tue 05 Sep 2023 02:21:25 PM CST
        Cups-PDF-1806           root          265443328   Tue 05 Sep 2023 02:21:27 PM CST
        Cups-PDF-1807           root          265443328   Tue 05 Sep 2023 02:21:29 PM CST
        Cups-PDF-1808           root          265443328   Tue 05 Sep 2023 02:21:32 PM CST
        Cups-PDF-1809           root          265443328   Tue 05 Sep 2023 02:21:36 PM CST
        Cups-PDF-1810           root          265443328   Tue 05 Sep 2023 02:21:46 PM CST
        Cups-PDF-1811           root          265443328   Tue 05 Sep 2023 02:21:47 PM CST
        Cups-PDF-1812           root          265443328   Tue 05 Sep 2023 02:21:50 PM CST
        Cups-PDF-1813           root          265443328   Tue 05 Sep 2023 02:21:53 PM CST
        Cups-PDF-1814           root          265443328   Tue 05 Sep 2023 02:21:55 PM CST

    Sample data returned::

        13

    Returns:
        int: the number of all queued jobs.

    Raises:
        SkipComponent: When there is not any content.
    """

    content = broker[LocalSpecsLpstatO.lpstat_o].content
    if content:
        result = []
        for line in content:
            if all(bad_keywords not in line for bad_keywords in ["no such file or directory", "not a directory", "command not found", "no module named", "no files found for", "missing dependencies:", "Bad file descripto"]):
                result.append(line)
        if result:
            return len(result)

    raise SkipComponent
