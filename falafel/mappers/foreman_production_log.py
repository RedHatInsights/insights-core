from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class LogLineList(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in one line
        """
        return any(s in l for l in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them in a list
        """
        return [l for l in self.data if s in l]


@mapper('foreman_production.log')
def foreman_production_log(context):
    """
    Returns an object in type of LogLineList which provide two methods:
    - Usage:
      in:
        log = shared.get(foreman_production_log)
        if "Abort command issued" in log:
            ...
      get:
        err_lines = log.get('[E]')
        for line in err_lines:
            ...
    -----------

    """
    return LogLineList(context.content)
