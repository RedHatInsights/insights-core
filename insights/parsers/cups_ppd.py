"""
CupsPpd - files ``/etc/cups/ppd/*``
===================================

Parser to parse the content of files ``/etc/cups/ppd/*``
"""

from insights import Parser
from insights import parser
from insights.specs import Specs


@parser(Specs.cups_ppd)
class CupsPpd(Parser):
    """
    Class to parse ``/etc/cups/ppd/*`` files.

    Sample output for files::

        *PPD-Adobe: "4.3"
        *FormatVersion: "4.3"
        *FileVersion: "2.2"
        *LanguageVersion: English
        *LanguageEncoding: ISOLatin1
        *cupsFilter2: "application/vnd.cups-pdf application/pdf 10 -"
        *cupsFilter2: "application/vnd.cups-postscript application/postscript 10 -"
        *cupsFilter2: "application/vnd.cups-banner application/vnd.cups-banner 10 -"

    Examples:
        >>> type(cups_ppd)
        <class 'insights.parsers.cups_ppd.CupsPpd'>
        >>> cups_ppd["PCFileName"]
        '"ippeve.ppd"'
        >>> cups_ppd["cupsFilter2"]
        ['"application/vnd.cups-pdf application/pdf 10 -"', '"application/vnd.cups-postscript application/postscript 10 -"']
    """
    def parse_content(self, content):
        self.data = {}
        for line in content:
            if "*" in line and ":" in line:
                key = line.split(":")[0].split("*")[-1].strip()
                value = line.split(":")[-1].strip()
                if key in self.data:
                    if isinstance(self.data[key], list):
                        self.data[key].append(value)
                    else:
                        self.data[key] = [self.data[key], value]
                else:
                    self.data[key] = value

    def __getitem__(self, item):
        return self.data[item]
