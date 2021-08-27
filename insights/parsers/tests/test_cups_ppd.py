from insights.tests import context_wrap
from insights.parsers import cups_ppd
from insights.parsers.cups_ppd import CupsPpd
import doctest

CUPS_PPD = """
*PPD-Adobe: "4.3"
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


def test_cups_ppd():
    cups_ppd_result = CupsPpd(context_wrap(CUPS_PPD, path='/etc/cups/ppd/NAY_10F_Smurfs.ppd'))
    assert cups_ppd_result["PCFileName"] == '"ippeve.ppd"'
    assert cups_ppd_result["cupsFilter2"] == ['"application/vnd.cups-pdf application/pdf 10 -"', '"application/vnd.cups-postscript application/postscript 10 -"']


def test_cups_ppd_documentation():
    env = {
        'cups_ppd': CupsPpd(context_wrap(CUPS_PPD,
            path='/etc/cups/ppd/NAY_10F_Smurfs.ppd'))
    }
    failed, total = doctest.testmod(cups_ppd, globs=env)
    assert failed == 0
