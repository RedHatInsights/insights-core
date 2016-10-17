from collections import namedtuple
from falafel.core.plugins import reducer
from falafel.mappers.redhat_release import RedhatRelease as rht_release
from falafel.mappers.uname import Uname

Release = namedtuple('Release', field_names=['major', 'minor'])


@reducer(requires=[[rht_release, Uname]], shared=True)
def redhat_release(local, shared):
    un = shared.get(Uname)
    if un:
        return Release(*un.release_tuple)

    rh_release = shared.get(rht_release)
    return Release(rh_release.major, rh_release.minor)
