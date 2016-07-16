from falafel.core.plugins import mapper


@mapper("current_clocksource")
def get_current_clksrc(context):
    """
    Return the current clock source in string
    """
    clksrc = list(context.content)[0]
    return clksrc
