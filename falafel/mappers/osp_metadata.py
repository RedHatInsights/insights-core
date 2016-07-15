from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class OSPRole(MapperOutput):

    def isDirector(self):
        return self["role"].lower() == "director"

    def isController(self):
        return self["role"].lower() == "controller"

    def isCompute(self):
        return self["role"].lower() == "compute"


@mapper("uname")
def osp_metadata_role(context):
    """
    As all platforms have 'uname' file, so use it to get osp role.
    return osp role for Openstack platform
    for non-osp machine, return None
    """
    if context.osp.role:
        return OSPRole({"role": context.osp.role})
