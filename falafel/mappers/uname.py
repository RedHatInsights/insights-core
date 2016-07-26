from falafel.core.plugins import mapper
from falafel.util.uname import Uname


@mapper('uname')
def uname(context):
    """
    return a Uname object from a uname string
    """
    line = list(context.content)[0]
    return Uname(line)
