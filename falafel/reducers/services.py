from falafel.core.plugins import reducer
from falafel.mappers import chkconfig
from falafel.mappers.systemd import unitfiles


class Services(object):
    def __init__(self, data):
        self.data = data

    def is_on(self, name):
        return self.data.get(name, self.data.get(name + '.service', False))


@reducer(requires=[[chkconfig.ChkConfig, unitfiles.UnitFiles]], shared=True)
def services(local, shared):
    chk = shared.get(chkconfig.ChkConfig)
    svc = shared.get(unitfiles.UnitFiles)
    data = {}
    if chk:
        data.update(chk.data)
    if svc:
        data.update(svc.data)
    return Services(data)
