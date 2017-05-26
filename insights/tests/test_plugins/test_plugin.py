from insights.core.plugins import reducer
from insights.mappers import installed_rpms, uname


@reducer(optional=[installed_rpms.InstalledRpms, uname.Uname])
def report(local, shared):
    pass
