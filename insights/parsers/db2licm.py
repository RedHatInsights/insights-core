"""
IBM DB2 Sever details
=====================

Module for the processing of output from the ``db2licm -l`` command.
"""
from insights.core.plugins import parser
from insights.core import CommandParser
from insights.parsers import ParseException, get_active_lines
from insights.specs import Specs


@parser(Specs.db2licm_l)
class DB2Info(CommandParser, dict):
    """
    This parser processes the output of the command `db2licm_l` and provides
    the information as a dictionary.

    Sample input::

        Product name:                     "DB2 Enterprise Server Edition"
        License type:                     "CPU Option"
        Expiry date:                      "Permanent"
        Product identifier:               "db2ese"
        Version information:              "9.7"
        Enforcement policy:               "Soft Stop"
        Features:
        DB2 Performance Optimization ESE: "Not licensed"
        DB2 Storage Optimization:         "Not licensed"
        DB2 Advanced Access Control:      "Not licensed"
        IBM Homogeneous Replication ESE:  "Not licensed"

        Product name:                     "DB2 Connect Server"
        Expiry date:                      "Expired"
        Product identifier:               "db2consv"
        Version information:              "9.7"
        Concurrent connect user policy:   "Disabled"
        Enforcement policy:               "Soft Stop"

    Example:

        >>> list(parser_result.keys())
        ['DB2 Enterprise Server Edition', 'DB2 Connect Server']
        >>> parser_result['DB2 Enterprise Server Edition']["Version information"]
        '9.7'

    Override the base class parse_content to parse the output of the '''db2licm -l'''  command.
    Information that is stored in the object is made available to the rule plugins.


    Raises:
        ParseException: raised if data is not parsable.
    """

    def parse_content(self, content):

        # name = None
        body = {}

        # Input data is available in text file. Reading each line in file and parsing it to a dictionary.
        for line in get_active_lines(content):
            if ':' in line:
                key, val = [i.strip() for i in line.strip().split(":", 1)]
                if key == "Features":
                    continue
            else:
                raise ParseException("Unable to parse db2licm info: {0}".format(content))

            if key == "Product name":
                body = {}
                self[val] = body
            else:
                body[key] = val

        if not self:
            # If no data is obtained in the command execution then throw an exception instead of returning an empty
            # object.  Rules depending solely on this parser will not be invoked, so they don't have to
            # explicitly check for invalid data.
            raise ParseException("Unable to parse db2licm info: {0}".format(content))
