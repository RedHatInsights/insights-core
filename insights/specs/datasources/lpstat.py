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
    lpstat_o = simple_command("/usr/bin/lpstat -o")
    """ Returns the output of command ``/usr/bin/lpstat -o`` """


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


@datasource(LocalSpecs.lpstat_o, HostContext)
def lpstat_queued_jobs_count(broker):
    """
    This datasource provides the count of all queued job.

    Typical content of ``/usr/bin/lpstat -o`` file is::

        Cups-PDF-1802           root          265443328   Tue 05 Sep 2023 02:21:19 PM CST
        Cups-PDF-1803           root          265443328   Tue 05 Sep 2023 02:21:21 PM CST
        Cups-PDF-1804           root          265443328   Tue 05 Sep 2023 02:21:22 PM CST

    Sample data returned::

        3

    Returns:
        DatasourceProvider: Returns the collected content containing the count of all queued jobs.

    Raises:
        SkipComponent: When there is not any content.
    """

    content = broker[LocalSpecs.lpstat_o].content
    if content:
        cnt = 0
        bad_lines = ["no such file or directory",
                     "not a directory",
                     "command not found",
                     "no module named",
                     "no files found for",
                     "missing dependencies:",
                     "Bad file descriptor"]
        for line in content:
            if not any(key in line for key in bad_lines):
                cnt += 1
        if cnt:
            return DatasourceProvider(content="{0}".format(cnt), relative_path='insights_commands/lpstat_-o_jobs_count')
    raise SkipComponent
