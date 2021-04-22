"""
Pmrep - command ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout``
==============================================================================================================

Parse the content of the ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout`` command.

Sample ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout`` command output::

    n.i.o.packets  n.i.o.packets  n.i.collisions  n.i.collisions  s.pagesout
             eth0             lo            eth0              lo
          count/s        count/s         count/s         count/s     count/s
              N/A            N/A             N/A             N/A         N/A
            1.997          0.000           0.000           0.000       0.000

Examples:
    >>> type(pmrep_doc_obj)
    <class 'insights.parsers.pmrep.PMREPMetrics'>
    >>> pmrep_doc_obj.data.get('n.i.o.packets', None)
    [{'eth0': '1.000'}, {'lo': '2.000'}]
    >>> pmrep_doc_obj.data.get('n.i.collisions', None)
    [{'eth0': '3.000'}, {'lo': '4.000'}]
    >>> pmrep_doc_obj.data.get('s.pagesout', None)
    ['5.000']
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.pmrep_metrics)
class PMREPMetrics(Parser):
    """Parses output of ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout`` command."""
    def parse_content(self, content):
        if not content:
            raise SkipException("Empty content.")

        heading_keys = ["n.i.o.packets", "n.i.collisions", "s.pagesout"]
        ignore_values = ["count/s", "N/A"]
        header_value = []
        self.data = {}

        for item in range(len(content)):
            content_data = content[item].split()
            if set(ignore_values).intersection(content_data):
                continue
            elif set(heading_keys).intersection(content_data):
                header_keys = content_data
            else:
                header_value.append(content_data)

        if len(header_value) > 0:
            data_keys = header_value[0]
            data_values = header_value[1]
            data_klist = []
            data_list = []

            datakeys_len = len(data_keys)
            for item in range(len(data_values)):
                if datakeys_len > 0:
                    # Create a key value pair
                    data_klist.append({data_keys[item]: data_values[item]})
                    datakeys_len -= 1
                else:
                    data_klist.append(data_values[item])

            datalist_len = len(data_klist)
            for item in range(len(header_keys)):
                if datalist_len > 1:
                    # If its the first entry or header key already exits
                    if len(self.data) == 0 or header_keys[item] in self.data:
                        data_list.append(data_klist[item])
                    else:
                        data_list = []
                        self.data[header_keys[item]] = [data_klist[item]]
                        data_list.append(data_klist[item])
                        continue
                    self.data[header_keys[item]] = data_list
                    datalist_len -= 1
            return self.data
