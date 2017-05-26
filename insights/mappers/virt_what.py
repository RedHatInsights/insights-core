from .. import Mapper, mapper

errors = ["virt-what: virt-what-cpuid-helper program not found in $PATH"]


@mapper('virt-what')
class VirtWhat(Mapper):

    @property
    def is_virtual(self):
        return self.generic != "Baremetal" and self.generic != 'Failed'

    @property
    def has_specific(self):
        return self.specific is not None and self.generic != self.specific

    def parse_content(self, content):
        if content and content[0] in errors:
            self.generic = 'Failed'
            self.specific = content[0]
        elif content:
            self.generic = content[0]
            self.specific = content[-1]
        else:
            self.generic = "Baremetal"
            self.specific = None
