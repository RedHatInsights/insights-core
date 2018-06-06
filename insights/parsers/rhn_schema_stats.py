from .. import parser, get_active_lines, CommandParser
from . import parse_delimited_table
from insights.specs import Specs


def _replace_tabs(s, ts=8):
    """
    Replace the tabs in 's' and keep its original alignment with the tab-stop
    equals to 'ts'
    """
    result = ''
    for c in s:
        if c == '\t':
            while True:
                result += ' '
                if len(result) % ts == 0:
                    break
        else:
            result += c
    return result


def _lower(s, ic=True):
    return s.lower() if ic else s


class Table(object):

    def __init__(self, data):
        self.data = data


class TableSummary(Table):

    def __contains__(self, s):
        return any(s in r.get('table', '').lower() for r in self.data)

    def get(self, s, ic):
        s = _lower(s, ic)
        return [r for r in self.data if s in _lower(r.get('table', ''), ic)]


class ConstraintTable(Table):

    def __contains__(self, s):
        return any(s in r.get('table', r.get('TABLE NAME', '')).lower() for r in self.data)

    def get(self, s, ic):
        s = _lower(s, ic)
        return [r for r in self.data if s in _lower(r.get('table', r.get('TABLE NAME', '')), ic)]


class LabelTable(Table):
    pass


@parser(Specs.rhn_schema_stats)
class DBStatsLog(CommandParser):
    """
    Returns a DBStatsLog object which provides below two methods:
    - in:
        Returns if specified string (ignore case) is contained in any table
        name
    - get_table(s, ic=True):
        Returns the table info in which the table name contains specified
        string (ignore case by default)


    === Sample of PostgreSQL ==================================================
     schema |             table              |   rows
    --------+--------------------------------+----------
     public | rhnsnapshotpackage             | 47428950
     ...
    (402 rows)

     name                | type | table              | src
    ---------------------+------+--------------------+--------------
     chkpb_probe_type_ck | c    | rhn_check_probe    | ((probe_type))
     chkpb_probe_type    | c    | log                |
     ...
    (1402 rows)

     label |  created   |  modified  |       name       | epoch | version  | release
    -------+------------+------------+------------------+-------+----------+---------
    schema | 2015-10-16 | 2015-10-16 | satellite-schema |       | 5.7.0.19 | 1.el6sat
     ...
    (11 rows)

    === Sample of ORACLE ======================================================
    PLAN_TABLE: 0
    PXTSESSIONS: 10
    QRTZ_BLOB_TRIGGERS: 0
    ...

    CONSTRAINT NAME   TYPE TABLE NAME   SEARCH CONDITION    REFERENCED CONSTRAINT
    ----------------- ---- ------------ ------------------- ---------------------
    SYS_C003030       C    PXTSESSIONS  "VALUE" IS NOT NULL
    PXT_SESSIONS_PK   P    PXTSESSIONS
    \t\t\t...'Product E
    PXTSESSIONS_USER  R    PXTSESSIONS                      WEB_CONTACT_PK
    ...

    LABEL   CREATED    MODIFIED   NAME             EPOCH  VERSION    RELEASE
    ------- ---------- ---------- ---------------- ------ ---------- --------
    schema  2014-05-01 2014-05-01 satellite-schema        5.5.0.22   1.el5sat
    ==========================================================================
    """

    def __contains__(self, s):
        """
        Return if the 's' (ignore case) is contained in any table name or not
        """
        s = s.lower()
        return s in self.data.get("table_summary", []) or s in self.data.get("constraint_table", [])

    def get_table(self, s, ic=True):
        """
        Return the table info in which the table name contains
        the 's'
        """
        result = self.data["table_summary"].get(s, ic) if "table_summary" in self.data else []
        result.extend(self.data["constraint_table"].get(s, ic) if "constraint_table" in self.data else [])
        return result

    def parse_content(self, content):
        tables = []
        table = []
        if content and content[0].strip().startswith("schema"):
            # for PostgreSQL db stats log
            for line in get_active_lines(content, comment_char="--"):
                if line.startswith("(") and "rows" in line:
                    tables.append(parse_delimited_table(table, delim="|"))
                    table = []
                else:
                    table.append(line)
        else:
            # for Oracle db stats log
            header_line = []
            header_list = []
            index_list = []
            for line in content:
                if line.strip() == '' or line.startswith('\t'):
                    pass
                elif ': ' in line:
                    k, _, v = line.partition(': ')
                    table.append({'table': k.strip(),
                                  'rows': int(v.strip())})
                elif line.startswith('LABEL') or line.startswith('CONSTRAINT '):
                    header_line = _replace_tabs(line)
                elif header_line and line.startswith('--'):
                    pre_idx = 0
                    for idx, c in enumerate(line):
                        if c == ' ':
                            header_list.append(header_line[pre_idx:idx].strip())
                            pre_idx = idx + 1
                            index_list.append(pre_idx)
                    header_list.append(header_line[pre_idx:].strip())
                    index_list.append(-1)
                    header_line = []
                elif line.startswith("PL/SQL procedure ") or " rows " in line:
                    tables.append(table)
                    table = []
                    index_list = []
                    header_list = []
                elif len(index_list) > 1:
                    line = _replace_tabs(line)
                    items_list = []
                    pre_idx = 0
                    for idx in index_list:
                        items_list.append(line[pre_idx:idx].strip())
                        pre_idx = idx
                    table.append(dict(zip(header_list, items_list)))
        if tables:
            self.data = {
                "table_summary": TableSummary(tables[0]) if len(tables) > 0 else None,
                "constraint_table": ConstraintTable(tables[1]) if len(tables) > 1 else None,
                "label_table": LabelTable(tables[2]) if len(tables) > 2 else None
            }
        else:
            self.data = {}
