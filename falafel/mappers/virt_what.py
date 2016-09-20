from .. import MapperOutput, mapper, computed


class VirtWhat(MapperOutput):

    @computed
    def is_virtual(self):
        return self["generic"] != "Baremetal"

    @computed
    def has_specific(self):
        return "specific" in self and self["generic"] != self["specific"]


@mapper('virt-what')
def virt_what(context):
    if context.content:
        return VirtWhat({
            "generic": context.content[0],
            "specific": context.content[-1]
        })
    else:
        return VirtWhat({"generic": "Baremetal"})
