"""
CupsPpd - files ``/etc/cups/ppd/*``
===================================

Parser to parse the content of files ``/etc/cups/ppd/*``
"""

from insights import Parser
from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.cups_ppd)
class CupsPpd(Parser, dict):
    """
    Class to parse ``/etc/cups/ppd/*`` files.

    Sample output for files::

        *PPD-Adobe: "4.3"
        *% Copyright 2007-2014 by Apple Inc.
        *% Copyright: 1997-2007 by Easy Software Products.
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

    Examples:
        >>> type(cups_ppd)
        <class 'insights.parsers.cups_ppd.CupsPpd'>
        >>> cups_ppd["PCFileName"]
        '"ippeve.ppd"'
        >>> cups_ppd["cupsFilter2"]
        ['"application/vnd.cups-pdf application/pdf 10 -"', '"application/vnd.cups-postscript application/postscript 10 -"']
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("No Valid Configuration")
        data = {}
        for line in content:
            if line.startswith("*") and ":" in line and not line.startswith("*%"):
                key = line.split(":")[0].split("*")[-1].strip()
                value = line.split(":")[-1].strip()
                if key in data:
                    if isinstance(data[key], list):
                        data[key].append(value)
                    else:
                        data[key] = [data[key], value]
                else:
                    data[key] = value
        if not data:
            raise SkipException("No Valid Configuration")
        self.update(data)
