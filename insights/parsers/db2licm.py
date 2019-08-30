"""
IBM DB2 Sever details
=====================

Module for the processing of output from the ``db2licm -l`` command.
Data is avaliable as rows of the output contained
in one ``Record`` object for each line of output.
"""
from insights.core.plugins import parser
from insights.core import CommandParser, LegacyItemAccess
from insights.parsers import ParseException, get_active_lines
from insights.specs import Specs


@parser(Specs.db2licm_l)
class DB2Info(LegacyItemAccess, CommandParser):
    """
    This parser processes the output of the command `db2licm_l` and provides
    the information as a dictionary.

    The LegacyItemAccess class provides some helper functions for dealing with a
    class having a `data` attribute.

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

        >>> parser_result.data.keys()
        dict_keys(['DB2 Enterprise Server Edition', 'DB2 Connect Server'])
        >>> parser_result.data['DB2 Enterprise Server Edition']
        {'License type': 'CPU Option', 'Expiry date': 'Permanent', 'Product identifier': 'db2ese', 'Version information': '9.7', 'Enforcement policy': 'Soft Stop', 'DB2 Performance Optimization ESE': 'Not licensed', 'DB2 Storage Optimization': 'Not licensed', 'DB2 Advanced Access Control': 'Not licensed', 'IBM Homogeneous Replication ESE': 'Not licensed'}
        >>> parser_result.data['DB2 Enterprise Server Edition']["Version information"]
        '9.7'

    Override the base class parse_content to parse the output of the '''db2licm -l'''  command.
    Information that is stored in the object is made available to the rule plugins.

    Attributes:
        data (dict): Dictionary containing each of the key:value pairs from the command
            output.

    Raises:
        ParseException: raised if data is not parsable.
    """

    def parse_content(self, content):

        # Stored data in a dictionary data structure
        self.data = {}

        name = None
        body = {}

        # Input data is available in text file. Reading each line in file and parsing it to a dictionary.
        for line in get_active_lines(content):
            if ':' in line:
                key, val = line.strip().split(":", 1)
                key = key.strip()
                val = val.lstrip()
                if key == "Features":
                    continue
            else:
                raise ParseException("Unable to parse db2licm info: {}".format(content))
            if key == "Product name":
                if name is None:
                    name = val
                else:
                    self.data[name] = body
                    name = val
                    body = {}
            else:
                body[key.strip()] = val.lstrip(" ")

        if name and body:
            self.data[name] = body

        if not self.data:
            # If no data is obtained in the command execution then throw an exception instead of returning an empty
            # object.  Rules depending solely on this parser will not be invoked, so they don't have to
            # explicitly check for invalid data.
            raise ParseException("Unable to parse db2licm info: {}".format(content))
