from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper("postgresql.conf")
class PostgreSQLConf(LegacyItemAccess, Mapper):
    """
    Parses postgresql.conf and returns a dict.
    - {
        "port": '5344'
        "listen_addresses": 'localhost'
      }
    """

    def parse_content(self, content):
        pg_dict = {}
        for line in get_active_lines(content):
            if '=' in line:
                key, _, value = line.partition("=")
                # In postgresql.conf, there are lines like:
                # - plog_line_prefix = '%m '
                # strip the " and ' (reserve the space inner the " or ')
                # {"plig_line_prefix": "%m "}; but not {"plig_line_prefix": "'%m '"}
                pg_dict[key.strip()] = value.strip().strip('\'"')
        self.data = pg_dict
