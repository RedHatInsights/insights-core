from falafel.core.plugins import mapper
from falafel.core.mapper import MapperOutput

class DmesgLineList(MapperOutput):

    def has_startswith(self, prefix):
        """
        Returns a boolean array which is `True` where there is one line in
        dmesg starts with `prefix`, otherwise `False`.
        """
        return any(line.startswith(prefix) for line in self.data)

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in dmesg output
        """
        return any(s in line for line in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in self.data if s in line]


@mapper('dmesg')
def dmesg(context):
    """
    Returns an object of DmesgLineList
    """
    return DmesgLineList(context.content)
