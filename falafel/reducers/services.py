from falafel.core.plugins import reducer
from falafel.mappers import chkconfig
from falafel.mappers.systemd import unitfiles


@reducer(requires=[[chkconfig.ChkConfig, unitfiles.UnitFiles]], shared=True)
class Services(object):
    def __init__(self, local, shared):
        self.data = {}
        chk = shared.get(chkconfig.ChkConfig)
        svc = shared.get(unitfiles.UnitFiles)
        if chk:
            self.data.update(chk.data)
        if svc:
            self.data.update(svc.data)

    def is_on(self, name):
        return self.data.get(name, self.data.get(name + '.service', False))
