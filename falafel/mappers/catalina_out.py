from falafel.core.plugins import mapper
from falafel.core import LogFileOutput


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
    return LogFileOutput(context.content, path=context.path)
