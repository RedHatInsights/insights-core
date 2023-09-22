"""
Custom datasources for ``ls`` commands
"""
from insights.core.context import HostContext
from insights.core.dr import get_name
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


def _list_items(spec):
    """Return a tuple of directories according to the spec filters."""
    filters = sorted(get_filters(spec))
    if filters:
        if len(filters) == 1 and 'R' not in get_name(spec).split('_')[-2]:
            """
            .. note::
                Insert a non-existing directory when there is only ONE target for
                the datasource to list, to make sure the directory be outputted.

                ==============================================================
                # list a single dir '/mnt'
                $ ls -lan /mnt
                total 0
                drwxr-xr-x.  2 0 0   6 Jun 21  2021 .
                dr-xr-xr-x. 17 0 0 224 Apr 17 16:45 ..
                --------------------------------------------------------------
                # list a single dir with this patch
                $ ls -lan /mnt _non_existing_
                ls: cannot access ' _non_existing_': No such file or directory
                /mnt:                      # <--<< the dir is outputted here
                total 0
                drwxr-xr-x.  2 0 0   6 Jun 21  2021 .
                dr-xr-xr-x. 17 0 0 224 Apr 17 16:45 ..
                ==============================================================
            """
            filters.append('_non_existing_')
        return ' '.join(filters)
    raise SkipComponent


@datasource(HostContext)
def list_with_la(broker):
    return _list_items(Specs.ls_la_dirs)


@datasource(HostContext)
def list_with_la_filtered(broker):
    return _list_items(Specs.ls_la_filtered_dirs)


@datasource(HostContext)
def list_with_lan(broker):
    return _list_items(Specs.ls_lan_dirs)


@datasource(HostContext)
def list_with_lan_filtered(broker):
    return _list_items(Specs.ls_lan_filtered_dirs)


@datasource(HostContext)
def list_with_lanL(broker):
    return _list_items(Specs.ls_lanL_dirs)


@datasource(HostContext)
def list_with_lanR(broker):
    return _list_items(Specs.ls_lanR_dirs)


@datasource(HostContext)
def list_with_lanRL(broker):
    return _list_items(Specs.ls_lanRL_dirs)


@datasource(HostContext)
def list_with_lanRZ(broker):
    return _list_items(Specs.ls_lanRZ_dirs)


@datasource(HostContext)
def list_with_lanZ(broker):
    return _list_items(Specs.ls_lanZ_dirs)
