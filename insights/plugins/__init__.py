from insights import condition
from insights.combiners.os_release import OSRelease


@condition(OSRelease)
def os_release_condition(osr):
    return "something"
