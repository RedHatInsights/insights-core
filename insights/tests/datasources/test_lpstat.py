import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.lpstat import LocalSpecs, lpstat_protocol_printers_info, LocalSpecsLpstatO, lpstat_queued_jobs_number


LPSTAT_V = """
device for test_printer1: ipp://cups.test.com/printers/test_printer1
device for test_printer2: ipp://cups.test.com/printers/test_printer2
device for test_printer3: socket://192.168.1.5:9100
device for test_printer4: usb://smth
device for test_printer5: ///dev/null
""".strip()

LPSTAT_V_NOT_GOOD = """
lpstat: Transport endpoint is not connected
""".strip()

LPSTAT_V_RESULT = """
device for test_printer1: ipp
device for test_printer2: ipp
device for test_printer3: socket
device for test_printer4: usb
device for test_printer5: ///dev/null
""".strip()

RELATIVE_PATH = 'insights_commands/lpstat_-v'

LPSTAT_O = """
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
""".strip()

LPSTAT_O_EMPTY = """
""".strip()

LPSTAT_O_INVALID = """
lpstat: Bad file descripto
""".strip()

LPSTAT_O_PATH = 'insights_commands/lpstat_-o'


def test_lpstat_datasource():
    lpstat_data = Mock()
    lpstat_data.content = LPSTAT_V.splitlines()
    broker = {LocalSpecs.lpstat_v: lpstat_data}
    result = lpstat_protocol_printers_info(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=LPSTAT_V_RESULT, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_lpstat_datasource_NG_output():
    lpstat_data = Mock()
    lpstat_data.content = LPSTAT_V_NOT_GOOD.splitlines()
    broker = {LocalSpecs.lpstat_v: lpstat_data}
    with pytest.raises(SkipComponent) as e:
        lpstat_protocol_printers_info(broker)
    assert 'SkipComponent' in str(e)


def test_lpstat_o():
    lpstat_o = Mock()
    lpstat_o.content = LPSTAT_O.splitlines()
    broker = {LocalSpecsLpstatO.lpstat_o: lpstat_o}
    result = lpstat_queued_jobs_number(broker)
    assert result is not None
    assert isinstance(result, int)
    assert result == 13


def test_lpstat_o_empty():
    lpstat_o = Mock()
    lpstat_o.content = LPSTAT_O_EMPTY.splitlines()
    broker = {LocalSpecsLpstatO.lpstat_o: lpstat_o}
    with pytest.raises(SkipComponent) as e:
        lpstat_queued_jobs_number(broker)
    assert 'SkipComponent' in str(e)


def test_lpstat_o_invalid():
    lpstat_o = Mock()
    lpstat_o.content = LPSTAT_O_INVALID.splitlines()
    broker = {LocalSpecsLpstatO.lpstat_o: lpstat_o}
    with pytest.raises(SkipComponent) as e:
        lpstat_queued_jobs_number(broker)
    assert 'SkipComponent' in str(e)
