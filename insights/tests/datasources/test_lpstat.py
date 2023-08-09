import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.lpstat import LocalSpecs, lpstat_protocol_printers_info


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
