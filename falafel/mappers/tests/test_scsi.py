from falafel.mappers.scsi import SCSI
from falafel.mappers import ParseException
from falafel.tests import context_wrap

import unittest

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


class TestSCSIMapper(unittest.TestCase):
    def test_parse(self):
        context = context_wrap(SCSI_OUTPUT)
        result = SCSI(context)
        self.assertEqual(len(result), 5)
        r = result[0]
        self.assertEqual(r.host, "scsi0")
        self.assertEqual(r.get('host'), 'scsi0')
        self.assertEqual(r.channel, "03")
        self.assertEqual(r.id, "00")
        self.assertEqual(r.lun, "00")
        self.assertEqual(r.vendor, "HP")
        self.assertEqual(r.model, "P420i")
        self.assertEqual(r.rev, "3.54")
        self.assertEqual(r.type, "RAID")
        self.assertEqual(r.ansi__scsi_revision, "05")

        r = result[1]
        self.assertEqual(r.model, "LOGICAL VOLUME")

        r = result[4]
        self.assertEqual(r.type, "Direct-Access")

        self.assertEqual([disc.vendor for disc in result], ['HP'] * 5)

    def test_single_spaced_ansi_scsi(self):
        result = SCSI(context_wrap(SCSI_OUTPUT_SINGLE_SPACED_ANSI_SCSI))
        self.assertEqual(len(result), 4)

    def test_missing_header(self):
        with self.assertRaisesRegexp(ParseException, 'Expected Header: Attached devices:'):
            result = SCSI(context_wrap(SCSI_OUTPUT_MISSING_HEADER))
            self.assertIsNone(result)
