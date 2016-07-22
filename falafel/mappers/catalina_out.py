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


@mapper('catalina.out')
def catalina_out(context):
    """
    Returns an object in type of LogLineList which provide two methods:
    - Usage:
      in:
        log = shared.get(tomcat_catalina_out)
        if "Abort command issued" in log:
            ...
      get:
        err_lines = log.get('KEY_WORDS')
        for line in err_lines:
            ...
    -----------

    """
    return LogLineList(context.content)
