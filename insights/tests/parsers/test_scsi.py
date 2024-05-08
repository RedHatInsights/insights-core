import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers.scsi import SCSI
from insights.tests import context_wrap


SCSI_OUTPUT = """
Attached devices:
Host: scsi0 Channel: 03 Id: 00 Lun: 00
  Vendor: HP       Model: P420i            Rev: 3.54
  Type:   RAID                             ANSI  SCSI revision: 05
Host: scsi0 Channel: 00 Id: 00 Lun: 00
  Vendor: HP       Model: LOGICAL VOLUME   Rev: 3.54
  Type:   Direct-Access                    ANSI  SCSI revision: 05
Host: scsi0 Channel: 00 Id: 00 Lun: 01
  Vendor: HP       Model: LOGICAL VOLUME   Rev: 3.54
  Type:   Direct-Access                    ANSI  SCSI revision: 05
Host: scsi0 Channel: 00 Id: 00 Lun: 02
  Vendor: HP       Model: LOGICAL VOLUME   Rev: 3.54
  Type:   Direct-Access                    ANSI  SCSI revision: 05
Host: scsi0 Channel: 00 Id: 00 Lun: 03
  Vendor: HP       Model: LOGICAL VOLUME   Rev: 3.54
  Type:   Direct-Access                    ANSI  SCSI revision: 05
"""

SCSI_OUTPUT_SINGLE_SPACED_ANSI_SCSI = """
Attached devices:
Host: scsi0 Channel: 00 Id: 00 Lun: 00
  Vendor: VMware   Model: Virtual disk     Rev: 1.0
  Type:   Direct-Access                    ANSI SCSI revision: 02
Host: scsi0 Channel: 00 Id: 01 Lun: 00
  Vendor: VMware   Model: Virtual disk     Rev: 1.0
  Type:   Direct-Access                    ANSI SCSI revision: 02
Host: scsi0 Channel: 00 Id: 02 Lun: 00
  Vendor: VMware   Model: Virtual disk     Rev: 1.0
  Type:   Direct-Access                    ANSI SCSI revision: 02
Host: scsi0 Channel: 00 Id: 03 Lun: 00
  Vendor: VMware   Model: Virtual disk     Rev: 1.0
  Type:   Direct-Access                    ANSI SCSI revision: 02
"""

SCSI_OUTPUT_MISSING_HEADER = """
Host: scsi0 Channel: 03 Id: 00 Lun: 00
  Vendor: HP       Model: P420i            Rev: 3.54
  Type:   RAID                             ANSI  SCSI revision: 05
"""

SCSI_OUTPUT_HAS_ONLY_HEADER = """
Attached devices:
"""

SCSI_OUTPUT_INNORMAL_VEMDOR_LINE = """
Attached devices:
Host: scsi0 Channel: 03 Id: 00 Lun: 00
  Vendor: HP       Model: P420i            Rev: 3.:
  Type:   RAID                             ANSI  SCSI revision: 05
"""

SCSI_OUTPUT_EMPTY = """
"""


def test_parse():
    context = context_wrap(SCSI_OUTPUT)
    result = SCSI(context)
    assert len(result) == 5
    r = result[0]
    assert r.host == "scsi0"
    assert r.get('host') == 'scsi0'
    assert r.channel == "03"
    assert r.id == "00"
    assert r.lun == "00"
    assert r.vendor == "HP"
    assert r.model == "P420i"
    assert r.rev == "3.54"
    assert r.type == "RAID"
    assert r.ansi__scsi_revision == "05"

    r = result[1]
    assert r.model == "LOGICAL VOLUME"

    r = result[4]
    assert r.type == "Direct-Access"

    assert [disc.vendor for disc in result] == ['HP'] * 5


def test_single_spaced_ansi_scsi():
    result = SCSI(context_wrap(SCSI_OUTPUT_SINGLE_SPACED_ANSI_SCSI))
    assert len(result) == 4


def test_missing_header():
    with pytest.raises(ParseException) as excinfo:
        result = SCSI(context_wrap(SCSI_OUTPUT_MISSING_HEADER))
        assert result is None
    assert 'Expected Header: Attached devices:' in str(excinfo.value)


def test_has_only_header():
    with pytest.raises(ParseException) as excinfo:
        result = SCSI(context_wrap(SCSI_OUTPUT_HAS_ONLY_HEADER))
        assert result is None
    assert 'Content has only header but no other content:' in str(excinfo.value)


def test_missing_innormal_rev():
    with pytest.raises(ParseException) as excinfo:
        result = SCSI(context_wrap(SCSI_OUTPUT_INNORMAL_VEMDOR_LINE))
        assert result is None
    assert 'Parse error for current line:' in str(excinfo.value)


def test_empty():
    with pytest.raises(SkipComponent) as excinfo:
        result = SCSI(context_wrap(SCSI_OUTPUT_EMPTY))
        assert result is None
    assert 'Empty content of file /proc/scsi/scsi' in str(excinfo.value)
