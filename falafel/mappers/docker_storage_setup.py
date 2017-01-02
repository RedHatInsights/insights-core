from .. import Mapper, mapper, get_active_lines
from ..mappers import split_kv_pairs


@mapper('docker_storage_setup')
class DockerStorageSetup(Mapper):
    """
    A mapper for accessing /etc/sysconfig/docker-storage-setup.
    """

    def __init__(self, *args, **kwargs):
        self.active_lines_unparsed = []
        self.active_settings = {}
        super(DockerStorageSetup, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content
        """
        self.active_lines_unparsed = get_active_lines(content)
        #  (man page specifies that a line must contain "=")
        self.active_settings = split_kv_pairs(content, use_partition=False)

    def __getitem__(self, item):
        return self.active_settings[item]

    def __contains__(self, item):
        return item in self.active_settings
