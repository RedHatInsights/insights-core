"""
CephOsdTreeText - command ``ceph osd tree``
===========================================
"""

from insights.specs import Specs
from insights import parser, CommandParser, LegacyItemAccess
from insights.parsers import ParseException, SkipException

text_to_json_header_map = {
    "ID": "id",
    "CLASS": "device_class",
    "WEIGHT": "crush_weight",
    "TYPE NAME": "type_name",
    "TYPE_NAME": "type_name",
    "STATUS": "status",
    "UP/DOWN": "status",
    "REWEIGHT": "reweight",
    "PRI-AFF": "primary_affinity",
    "PRIMARY-AFFINITY": "primary_affinity"
}


@parser(Specs.ceph_osd_tree_text)
class CephOsdTreeText(CommandParser, LegacyItemAccess):
    """
    Class to parse the output of command ``ceph osd tree``.

    The typical content is::

        ID CLASS WEIGHT  TYPE NAME       STATUS REWEIGHT PRI-AFF
        -1       0.08752 root default
        -9       0.02917     host ceph1
         2   hdd 0.01459         osd.2       up  1.00000 1.00000
         5   hdd 0.01459         osd.5       up  1.00000 1.00000
        -5       0.02917     host ceph2
         1   hdd 0.01459         osd.1       up  1.00000 1.00000
         4   hdd 0.01459         osd.4       up  1.00000 1.00000
        -3       0.02917     host ceph3
         0   hdd 0.01459         osd.0       up  1.00000 1.00000
         3   hdd 0.01459         osd.3       up  1.00000 1.00000
        -7             0     host ceph_1

    Examples:

        >>> ceph_osd_tree_text['nodes'][0]['id']
        '-1'
        >>> ceph_osd_tree_text['nodes'][0]['name']
        'default'
        >>> ceph_osd_tree_text['nodes'][0]['type']
        'root'
        >>> ceph_osd_tree_text['nodes'][3]['type']
        'osd'
    """

    def parse_content(self, content):
        def calc_column_indices(line, headers):
            idx = []
            for h in headers:
                i = idx[-1] + 1 if idx else 0
                idx.append(line.index(h, i))
            return idx

        if not content:
            raise SkipException("Empty content.")
        if len(content) == 1 or "TYPE NAME" not in content[0]:
            raise ParseException("Wrong content in table: '{0}'.".format(content))

        header = content[0].replace('TYPE NAME', 'TYPE_NAME')

        col_headers = header.strip().split()
        json_headers = [text_to_json_header_map[h] for h in col_headers]
        col_index = calc_column_indices(header, col_headers)

        name_header_index = header.index("TYPE_NAME")
        parents = []
        nodes = []
        for row_num, line in enumerate(content[1:]):
            node = dict(
                (json_headers[c], line[col_index[c]:col_index[c + 1]].strip())
                for c in range(len(col_index) - 1)
            )
            node[json_headers[-1]] = line[col_index[-1]:].strip()

            # update parent's children list
            name_index = line.index(node['type_name'])
            shift = (name_index - name_header_index) / 4
            if shift == 0:
                pass
            elif shift > len(parents):
                prev_line = row_num - 1
                parents.append(prev_line)
                nodes[parents[-1]]['children'].insert(0, int(node['id']))
            elif shift == len(parents):
                nodes[parents[-1]]['children'].insert(0, int(node['id']))
            elif shift < len(parents):
                parents.pop()
                nodes[parents[-1]]['children'].insert(0, int(node['id']))
            # update type name
            type_name = node.pop('type_name').split()
            node['type'] = type_name[0] if len(type_name) > 1 else type_name[0].split('.')[0]
            node['name'] = type_name[-1]
            nodes.append(node)
            # update children list for the none leave node
            if len(type_name) > 1:
                node['children'] = []
        self.data = {'nodes': nodes}
