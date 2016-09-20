from .. import mapper


@mapper('ksmstate')
def is_running(context):
    """
    Check if KSM is running. Returns 'True' or 'False'
    """
    ksminfo = {}
    ksminfo['running'] = False
    if context.content[0].split()[0] == '1':
        ksminfo['running'] = True
    return ksminfo
