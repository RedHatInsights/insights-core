from collections import namedtuple
from falafel.core.plugins import reducer
from falafel.mappers.redhat_release import RedhatRelease as rht_release
from falafel.mappers.uname import Uname

Release = namedtuple("Release", field_names=["major", "minor"])


@reducer(requires=[[rht_release, Uname]], shared=True)
def redhat_release(local, shared):
    """Check uname and redhat-release for rhel major/minor version.

    Prefer uname to redhat-release.

    Parameters
    ----------
    local : dict
        Only here for backward compat.  Should always be None.
    shared : dict
        A dictionary containing Uname and/or RedhatRelease classes
        as keys with instances of Uname or RedhatRelease as values.

    Returns
    -------
    Release
        A named tuple with `major` and `minor` version components.

    Raises
    ------
    Exeption
        If the version can't be determined even though a Uname or
        RedhatRelease was provided.
    """

    un = shared.get(Uname)
    if un and un.release_tuple[0] != -1:
        return Release(*un.release_tuple)

    rh_release = shared.get(rht_release)
    if rh_release:
        return Release(rh_release.major, rh_release.minor)

    raise Exception("Unabled to determine release.")
