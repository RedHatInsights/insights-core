from .. import Mapper, mapper, get_active_lines
from ..mappers import split_kv_pairs


@mapper('auditd.conf')
class AuditdConf(Mapper):
    """
    A mapper for accessing /etc/audit/auditd.conf.
    """

    def __init__(self, *args, **kwargs):
        self.active_lines_unparsed = []
        self.active_settings = {}
        super(AuditdConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content
        """
        self.active_lines_unparsed = get_active_lines(content)
        #  (man page specifies that a line must contain "=")
        self.active_settings = split_kv_pairs(content, use_partition=False)

    def get_active_setting_value(self, setting_name):
        """
        Access active setting value by setting name.

        Args:
            setting_name (string): Setting name
        """
        return self.active_settings[setting_name]
