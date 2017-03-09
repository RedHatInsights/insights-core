from falafel.core.plugins import reducer
from falafel.mappers import installed_rpms, uname


@reducer(optional=[installed_rpms.InstalledRpms, uname.Uname])
def report(local, shared):
    pass
