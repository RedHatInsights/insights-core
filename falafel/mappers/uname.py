from falafel.core.plugins import mapper
from falafel.util.uname import Uname


@mapper('uname')
def uname(context):
    """
    Return a dict which contains:
    - 'rhel_version': context.version
    - 'rhel_release': context.release
    - 'uname': an Instance of Uname
    """
    line = list(context.content)[0]
    return {
        'uname': Uname(line),
        'rhel_release': context.release,
        'rhel_version': context.version
    }
