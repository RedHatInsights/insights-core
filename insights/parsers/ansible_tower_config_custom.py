"""
AnsibleTowerConfigCustom - file ``/etc/tower/conf.d/custom.py``
===============================================================
The AnsibleTowerConfigCustom class parses the file ``/etc/tower/conf.d/custom.py``.
"""
import json
from .. import parser, get_active_lines, Parser, LegacyItemAccess
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.ansible_tower_config_custom)
class AnsibleTowerConfigCustom(Parser, LegacyItemAccess):
    """
    Class for content of ansible tower config file /etc/tower/conf.d/custom.py.

    Sample ``/etc/tower/conf.d/custom.py`` file::

        AWX_CLEANUP_PATHS = False
        AUTH_LDAP_GLOBAL_OPTIONS = {
            ldap.OPT_REFERRALS: False,
        }
        LOGGING['handlers']['tower_warnings']['level'] = 'DEBUG'

    Examples::
    >>> type(conf)
    <class 'insights.parsers.ansible_tower_config_custom.AnsibleTowerConfigCustom'>
    >>> conf["LOGGING['handlers']['tower_warnings']['level']"]
    'DEBUG'
    >>> conf['AUTH_LDAP_GLOBAL_OPTIONS']['ldap.OPT_REFERRALS']
    False
    >>> conf['AWX_CLEANUP_PATHS']
    False
    """

    def parse_content(self, content):
        """Parse content of of ansible tower config file '/etc/tower/conf.d/custom.py'"""
        self.data = {}
        json_lines = []
        section_key = ""
        brace_count = 0
        for line in get_active_lines(content):
            if not section_key:
                if "=" in line:
                    if "{" not in line:
                        key, value = [i.strip() for i in line.split('=', 1)]
                        if value.startswith("'") or value.startswith('"'):
                            value = value[1:]
                        if value.endswith("'") or value.endswith('"'):
                            value = value[:-1]
                        if value == "False":
                            value = False
                        if value == "True":
                            value = True
                        self.data[key] = value
                    else:
                        section_key, value = [i.strip() for i in line.split('=', 1)]
                        json_lines.append(value)
                        brace_count += 1
            else:
                # Convert {} content to JSON format
                line = line.replace("'", '"')
                line = line.replace('"""', '"')
                line = line.replace("False", "false")
                line = line.replace("True", "true")
                if ":" in line:
                    if "'" not in line and '"' not in line and '"""' not in line:
                        old_string = line.split(":")[0].strip()
                        new_string = '"' + old_string + '"'
                        line = line.replace(old_string, new_string)
                brace_count = brace_count + line.count("{")
                brace_count = brace_count - line.count("}")
                json_lines.append(line.strip())
                if brace_count == 0:
                    total_line = "".join(json_lines)
                    result_line = ""
                    for i in range(len(total_line)):
                        if total_line[i] == ",":
                            left_brace_index = i + 1
                            if left_brace_index < len(total_line) and total_line[left_brace_index] == "}":
                                continue
                        result_line = result_line + total_line[i]
                    try:
                        value = json.loads(result_line)
                    except ValueError:
                        raise SkipException('Syntax error')
                    self.data[section_key] = value
                    json_lines = []
                    section_key = ""
