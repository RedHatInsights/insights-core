from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper("cobbler_modules.conf")
class CobblerModulesConf(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        """
        Parses cobbler/modules.conf and returns a dict.
        - {
            "authentication": {"module":"authn_spacewalk"},
            "authorization": {"module":"authz_allowall"}
          }
        """
        modules_dict = {}
        section_dict = {}
        for line in get_active_lines(content):
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                modules_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, _, value = line.partition("=")
                section_dict[key.strip()] = value.strip()
        self.data = modules_dict
