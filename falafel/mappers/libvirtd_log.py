from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class ParseLibvirtdLog(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string s is contained in file libvirtd.log
        """
        return any(s in line for line in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in self.data if s in line]


@mapper('libvirtd.log')
def parse_libvirtd_log(context):
    return ParseLibvirtdLog(context.content)
