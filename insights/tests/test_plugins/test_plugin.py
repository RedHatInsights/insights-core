from insights.core.plugins import rule
from insights.parsers import installed_rpms, uname


@rule(optional=[installed_rpms.InstalledRpms, uname.Uname])
def report(local, shared):
    pass
