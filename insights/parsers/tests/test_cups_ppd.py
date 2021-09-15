from insights.tests import context_wrap
from insights.parsers import cups_ppd
from insights.parsers.cups_ppd import CupsPpd, SkipException
import doctest
import pytest


CUPS_PPD = """
*PPD-Adobe: "4.3"
*% Copyright 2007-2014 by Apple Inc.
*% test: this line is used to check comment
*FormatVersion: "4.3"
*FileVersion: "2.2"
*LanguageVersion: English
*LanguageEncoding: ISOLatin1
*PCFileName: "ippeve.ppd"
*Manufacturer: "Canon"
*ModelName: "iR-ADV C3525/3530 PPD"
*Product: "(iR-ADV C3525/3530 PPD)"
*NickName: "iR-ADV C3525/3530 PPD"
*ShortNickName: "iR-ADV C3525/3530 PPD"
*cupsFilter2: "application/vnd.cups-pdf application/pdf 10 -"
*cupsFilter2: "application/vnd.cups-postscript application/postscript 10 -"
""".strip()

CUPS_PPD_INVALID1 = '''
'''.strip()

CUPS_PPD_INVALID2 = '''
ShortNickName
'''.strip()


def test_cups_ppd():
    cups_ppd_result = CupsPpd(context_wrap(CUPS_PPD, path='/etc/cups/ppd/test_printer1.ppd'))
    assert cups_ppd_result["PCFileName"] == '"ippeve.ppd"'
    assert cups_ppd_result["cupsFilter2"] == ['"application/vnd.cups-pdf application/pdf 10 -"', '"application/vnd.cups-postscript application/postscript 10 -"']
    assert "test" not in cups_ppd_result

    with pytest.raises(SkipException) as exc:
        CupsPpd(context_wrap(CUPS_PPD_INVALID1, path='/etc/cups/ppd/test_printer1.ppd'))
    assert 'No Valid Configuration' in str(exc)

    with pytest.raises(SkipException) as exc:
        CupsPpd(context_wrap(CUPS_PPD_INVALID2, path='/etc/cups/ppd/test_printer1.ppd'))
    assert 'No Valid Configuration' in str(exc)


def test_cups_ppd_documentation():
    env = {
        'cups_ppd': CupsPpd(context_wrap(CUPS_PPD,
            path='/etc/cups/ppd/test_printer1.ppd'))
    }
    failed, total = doctest.testmod(cups_ppd, globs=env)
    assert failed == 0
