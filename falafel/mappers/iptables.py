from falafel.core.plugins import mapper
from falafel.core.mapper import MapperOutput
from falafel.mappers import get_active_lines


class Iptables(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in
        etc/sysconfig/iptables
        """
        return any(s in line for line in get_active_lines(self.data))

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in get_active_lines(self.data) if s in line]


@mapper('iptables')
def iptables_rule(context):
    """
    Returns an object of Iptables
    """
    return Iptables(context.content)
